"""
Procesador batch con pipeline Ovito integrado - VERSIÓN CORREGIDA
Aplica ConstructSurfaceModifier, InvertSelection, DeletedSelection antes de extraer features
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Callable
import logging
import threading
import tempfile
import os
import shutil  # CORREGIDO: Agregado import faltante
from dataclasses import asdict

# Importar módulos de Ovito con manejo de errores
try:
    from ovito.io import import_file, export_file
    from ovito.modifiers import (
        ConstructSurfaceModifier,
        InvertSelectionModifier, 
        DeleteSelectedModifier
    )
    OVITO_AVAILABLE = True
except ImportError as e:
    OVITO_AVAILABLE = False
    OVITO_IMPORT_ERROR = str(e)

# Importar módulos refactorizados existentes
from .config import ProcessingConfig, FeatureMode
from .file_parser import LAMMPSFileParser
from .enhanced_safe_feature_extractor import EnhancedSafeFeatureExtractor
from .data_leakage_detector import DataLeakageDetector

logger = logging.getLogger(__name__)


class OvitoIntegratedBatchProcessor:
    """
    Procesador batch con pipeline Ovito integrado para eliminación de superficie
    
    Pipeline:
    1. Cargar archivo dump con Ovito
    2. Aplicar ConstructSurfaceModifier para identificar superficie
    3. Aplicar InvertSelectionModifier para seleccionar interior
    4. Aplicar DeleteSelectedModifier para eliminar superficie
    5. Extraer features solo de átomos del interior
    6. Calcular vacancies usando atm_total original
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        # CORREGIDO: Validar que Ovito esté disponible
        if not OVITO_AVAILABLE:
            raise ImportError(f"Ovito no está disponible: {OVITO_IMPORT_ERROR}. "
                            "Instale Ovito o use el procesador tradicional.")
        
        self.config = config or ProcessingConfig()
        
        # Configuración específica de Ovito
        self.surface_radius = 2.5  # Radio para ConstructSurfaceModifier
        self.smoothing_level = 8   # Nivel de suavizado
        
        # Inicializar componentes especializados
        self.file_parser = LAMMPSFileParser()
        self.feature_extractor = EnhancedSafeFeatureExtractor(self.config)
        self.leakage_detector = DataLeakageDetector()
        
        # Callback para progreso
        self.progress_callback: Optional[Callable] = None
        
        # Estado del procesamiento
        self._stop_requested = False
        
        # Directorio temporal para archivos procesados
        self.temp_dir = None
        
        # CORREGIDO: Lista de columnas esperadas con fallbacks
        self.default_columns = [
            "Particle Identifier",
            "Particle Type", 
            "Position.X",
            "Position.Y",
            "Position.Z"
        ]
        
        self.optional_columns = [
            "c_peatom",
            "c_satom[1]", "c_satom[2]", "c_satom[3]", 
            "c_satom[4]", "c_satom[5]", "c_satom[6]",
            "c_coord",
            "c_voro[1]"
        ]
    
    def set_ovito_parameters(self, surface_radius: float = 2.5, smoothing_level: int = 8):
        """Configurar parámetros específicos de Ovito"""
        if surface_radius <= 0:
            raise ValueError("surface_radius debe ser positivo")
        if smoothing_level < 0:
            raise ValueError("smoothing_level debe ser no negativo")
            
        self.surface_radius = surface_radius
        self.smoothing_level = smoothing_level
        logger.info(f"Parámetros Ovito actualizados: radius={surface_radius}, smoothing={smoothing_level}")
    
    def set_parameters(self, **kwargs):
        """Actualizar parámetros de configuración"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Actualizado {key} = {value}")
        
        # Recrear feature extractor con nueva configuración
        self.feature_extractor = EnhancedSafeFeatureExtractor(self.config)
    
    def set_feature_mode(self, mode: FeatureMode):
        """Establecer modo de extracción de features"""
        self.config.feature_mode = mode
        self.feature_extractor = EnhancedSafeFeatureExtractor(self.config)
        logger.info(f"Modo de features establecido: {mode.value}")
    
    def set_progress_callback(self, callback: Callable):
        """Establecer callback para reportar progreso"""
        self.progress_callback = callback
    
    def process_directory(self, directory: str, 
                         validate_leakage: bool = True,
                         save_intermediate: bool = False) -> pd.DataFrame:
        """
        Procesar directorio completo con pipeline Ovito integrado
        
        Args:
            directory: Directorio con archivos .dump
            validate_leakage: Si validar fuga de información
            save_intermediate: Si guardar resultados intermedios
            
        Returns:
            DataFrame con features extraídas de átomos interiores
        """
        self._stop_requested = False
        
        # CORREGIDO: Crear directorio temporal de forma más segura
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="ovito_batch_", suffix="_temp")
            logger.debug(f"Directorio temporal creado: {self.temp_dir}")
        except Exception as e:
            raise RuntimeError(f"No se pudo crear directorio temporal: {str(e)}")
        
        try:
            # Encontrar archivos dump
            dump_files = self.file_parser.find_dump_files(directory)
            
            if not dump_files:
                raise ValueError(f"No se encontraron archivos .dump en {directory}")
            
            logger.info(f"Encontrados {len(dump_files)} archivos .dump")
            logger.info(f"Pipeline Ovito: ConstructSurface -> InvertSelection -> DeleteSelected")
            logger.info(f"Parámetros: radius={self.surface_radius}, smoothing={self.smoothing_level}")
            
            self._report_progress(0, len(dump_files), "Iniciando procesamiento con Ovito...")
            
            # Procesar archivos
            results = []
            errors = []
            
            for i, file_path in enumerate(dump_files, 1):
                if self._stop_requested:
                    logger.info("Procesamiento detenido por usuario")
                    break
                
                try:
                    file_name = Path(file_path).name
                    self._report_progress(i, len(dump_files), f"Procesando {file_name} con Ovito")
                    
                    # Procesar archivo individual con Ovito
                    features = self._process_single_file_with_ovito(file_path)
                    features["file"] = file_name
                    features["file_path"] = file_path
                    
                    results.append(features)
                    
                    # Log del resultado
                    n_atoms_interior = features.get('_n_atoms_interior', 'N/A')
                    n_atoms_original = features.get('_n_atoms_original', 'N/A')
                    n_features = len([k for k in features.keys() 
                                    if not k.startswith('_') and k not in ['file', 'file_path', 'file_hash', 'vacancies']])
                    
                    logger.info(f"✓ {file_name}: {n_atoms_original}→{n_atoms_interior} átomos (eliminó superficie), {n_features} features")
                    
                except Exception as e:
                    error_msg = f"Error en {Path(file_path).name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            if not results:
                raise RuntimeError("No se pudieron procesar archivos correctamente")
            
            # Crear dataset
            dataset = pd.DataFrame(results).set_index("file").sort_index()
            
            # Log de summary
            self._log_ovito_processing_summary(dataset)
            
            # Validar fuga de información si está habilitado
            if validate_leakage:
                self._validate_and_clean_dataset(dataset)
            
            # Guardar intermedios si está habilitado
            if save_intermediate:
                self._save_intermediate_results(dataset, directory)
            
            # Reporte final
            self._generate_final_report(dataset, errors)
            
            return dataset
            
        finally:
            # CORREGIDO: Limpiar directorio temporal siempre
            self._cleanup_temp_dir()
    
    def _get_available_columns(self, file_path: str) -> List[str]:
        """CORREGIDO: Detectar columnas disponibles en el archivo"""
        try:
            # Cargar archivo para inspeccionar columnas disponibles
            pipeline = import_file(file_path)
            data = pipeline.compute()
            
            available_columns = self.default_columns.copy()
            
            # Verificar columnas opcionales
            for col in self.optional_columns:
                if col in data.particles.keys():
                    available_columns.append(col)
                else:
                    logger.debug(f"Columna {col} no disponible en {file_path}")
            
            return available_columns
            
        except Exception as e:
            logger.warning(f"Error detectando columnas en {file_path}: {str(e)}")
            return self.default_columns
    
    def _process_single_file_with_ovito(self, file_path: str) -> Dict[str, Any]:
        """CORREGIDO: Procesar un archivo individual con pipeline Ovito completo"""
        
        # 1. Cargar archivo original para obtener número total de átomos
        df_original, n_atoms_original, metadata_original = self.file_parser.parse_last_frame(file_path)
        
        if df_original.empty or n_atoms_original <= 0:
            raise ValueError(f"Archivo original inválido: {n_atoms_original} átomos")
        
        # 2. Aplicar pipeline Ovito
        temp_file = None
        try:
            # CORREGIDO: Detectar columnas disponibles
            available_columns = self._get_available_columns(file_path)
            
            # Importar archivo con Ovito
            pipeline = import_file(file_path)
            
            # Aplicar modificadores en secuencia
            # Paso 1: Identificar superficie
            pipeline.modifiers.append(ConstructSurfaceModifier(
                radius=self.surface_radius,
                smoothing_level=self.smoothing_level,
                identify_regions=True,
                select_surface_particles=True
            ))
            
            # Paso 2: Invertir selección (seleccionar interior)
            pipeline.modifiers.append(InvertSelectionModifier())
            
            # Paso 3: Eliminar selección (eliminar superficie)
            pipeline.modifiers.append(DeleteSelectedModifier())
            
            # CORREGIDO: Crear archivo temporal con nombre único
            temp_file = os.path.join(
                self.temp_dir, 
                f"processed_{Path(file_path).stem}_{id(pipeline)}.dump"
            )
            
            # CORREGIDO: Exportar solo columnas disponibles
            export_file(
                pipeline,
                temp_file,
                "lammps/dump",
                columns=available_columns
            )
            
            # Verificar que el archivo se creó correctamente
            if not os.path.exists(temp_file):
                raise RuntimeError(f"No se pudo crear archivo temporal: {temp_file}")
            
            # 3. Parsear archivo procesado
            df_processed, n_atoms_interior, metadata_processed = self.file_parser.parse_last_frame(temp_file)
            
            if df_processed.empty or n_atoms_interior <= 0:
                raise ValueError(f"Datos procesados inválidos: {n_atoms_interior} átomos interiores")
            
            # 4. Extraer features usando solo átomos interiores
            features = self.feature_extractor.extract_features(df_processed, n_atoms_interior, metadata_processed)
            
            # 5. Recalcular vacancies usando número total original
            vacancies_real = int(self.config.atm_total - n_atoms_original)
            features["vacancies"] = vacancies_real
            
            # 6. Agregar metadata de procesamiento Ovito
            features["_n_atoms_original"] = n_atoms_original
            features["_n_atoms_interior"] = n_atoms_interior  
            features["_atoms_removed_surface"] = n_atoms_original - n_atoms_interior
            features["_surface_removal_ratio"] = float((n_atoms_original - n_atoms_interior) / n_atoms_original)
            features["_processing_mode"] = f"{self.config.feature_mode.value}_ovito"
            features["_ovito_radius"] = self.surface_radius
            features["_ovito_smoothing"] = self.smoothing_level
            features["_extractor_version"] = "EnhancedSafeFeatureExtractor_Ovito"
            features["_ovito_processing_success"] = True
            
            return features
            
        except Exception as e:
            logger.error(f"Error en pipeline Ovito para {file_path}: {str(e)}")
            # CORREGIDO: Fallback mejorado - usar datos originales
            logger.warning(f"Usando datos originales sin procesamiento Ovito para {file_path}")
            
            try:
                features = self.feature_extractor.extract_features(df_original, n_atoms_original, metadata_original)
                features["_n_atoms_original"] = n_atoms_original
                features["_n_atoms_interior"] = n_atoms_original
                features["_atoms_removed_surface"] = 0
                features["_surface_removal_ratio"] = 0.0
                features["_ovito_processing_success"] = False
                features["_ovito_error"] = str(e)
                return features
            except Exception as fallback_error:
                raise RuntimeError(f"Error en fallback para {file_path}: {str(fallback_error)}")
        
        finally:
            # CORREGIDO: Limpiar archivo temporal individual
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"No se pudo eliminar archivo temporal {temp_file}: {str(e)}")
    
    def _log_ovito_processing_summary(self, dataset: pd.DataFrame):
        """Log del resumen de procesamiento Ovito"""
        if '_atoms_removed_surface' in dataset.columns:
            surface_atoms_removed = dataset['_atoms_removed_surface']
            removal_ratios = dataset['_surface_removal_ratio']
            
            logger.info(f"OVITO PROCESSING SUMMARY:")
            logger.info(f"  Archivos procesados: {len(dataset)}")
            logger.info(f"  Átomos de superficie removidos promedio: {surface_atoms_removed.mean():.1f}")
            logger.info(f"  Ratio de remoción promedio: {removal_ratios.mean():.2%}")
            logger.info(f"  Rango de átomos removidos: {surface_atoms_removed.min()}-{surface_atoms_removed.max()}")
            
            # CORREGIDO: Verificar éxito de procesamiento Ovito
            if '_ovito_processing_success' in dataset.columns:
                success_rate = dataset['_ovito_processing_success'].mean()
                logger.info(f"  Tasa de éxito Ovito: {success_rate:.1%}")
                if success_rate < 1.0:
                    failed_count = (~dataset['_ovito_processing_success']).sum()
                    logger.warning(f"  Archivos con fallo en Ovito: {failed_count}")
        
        # Log de features generadas
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
        logger.info(f"  Total features extraídas: {len(feature_cols)}")
    
    def _validate_and_clean_dataset(self, dataset: pd.DataFrame):
        """Validar y limpiar dataset para evitar fuga"""
        logger.info("Validando dataset contra fuga de información...")
        
        try:
            # Detectar posible fuga
            leakage_analysis = self.leakage_detector.detect_leakage(dataset)
            
            if "error" in leakage_analysis:
                logger.warning(f"Error en análisis de fuga: {leakage_analysis['error']}")
                return
            
            # Eliminar features de alto riesgo automáticamente
            high_risk_features = leakage_analysis['high_risk_features']
            if high_risk_features:
                features_to_remove = [f['feature'] for f in high_risk_features]
                
                logger.warning(f"Eliminando {len(features_to_remove)} features de alto riesgo:")
                for feature_info in high_risk_features[:5]:
                    logger.warning(f"  - {feature_info['feature']}: r={feature_info['correlation']:.3f}")
                
                # Eliminar del dataset
                dataset.drop(columns=features_to_remove, inplace=True, errors='ignore')
            
            # Eliminar features prohibidas explícitamente
            forbidden_found = [col for col in self.config.forbidden_features 
                              if col in dataset.columns]
            if forbidden_found:
                dataset.drop(columns=forbidden_found, inplace=True)
                logger.info(f"Eliminadas features prohibidas: {forbidden_found}")
                
        except Exception as e:
            logger.error(f"Error en validación de fuga: {str(e)}")
    
    def _save_intermediate_results(self, dataset: pd.DataFrame, directory: str):
        """Guardar resultados intermedios con info de Ovito"""
        try:
            output_dir = Path(directory) / "processing_output_ovito"
            output_dir.mkdir(exist_ok=True)
            
            # Separar features de metadata
            feature_cols = [col for col in dataset.columns 
                           if not col.startswith('_') and col not in ['file_path', 'file_hash']]
            metadata_cols = [col for col in dataset.columns if col.startswith('_')]
            
            # Guardar features
            features_path = output_dir / "enhanced_features_ovito.csv"
            dataset[feature_cols].to_csv(features_path)
            
            # Guardar metadata de Ovito separadamente
            if metadata_cols:
                metadata_path = output_dir / "ovito_metadata.csv"
                dataset[metadata_cols].to_csv(metadata_path)
            
            # Guardar resumen de features mejoradas
            feature_summary = self.feature_extractor.get_feature_summary()
            feature_summary['ovito_processing'] = {
                'surface_radius': self.surface_radius,
                'smoothing_level': self.smoothing_level,
                'processing_type': 'surface_removal'
            }
            
            summary_path = output_dir / "feature_summary_ovito.json"
            import json
            with open(summary_path, 'w') as f:
                json.dump(feature_summary, f, indent=2)
            
            # Guardar configuración completa
            config_path = output_dir / "processing_config_ovito.json"
            config_dict = asdict(self.config)
            config_dict['ovito_parameters'] = {
                'surface_radius': self.surface_radius,
                'smoothing_level': self.smoothing_level
            }
            config_dict['extractor_type'] = 'EnhancedSafeFeatureExtractor_Ovito'
            
            with open(config_path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            logger.info(f"Resultados intermedios con Ovito guardados en {output_dir}")
            
        except Exception as e:
            logger.error(f"Error guardando resultados intermedios: {str(e)}")
    
    def _generate_final_report(self, dataset: pd.DataFrame, errors: List[str]):
        """Generar reporte final del procesamiento con Ovito"""
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
        
        total_files = len(dataset)
        total_features = len(feature_cols)
        
        # Estadísticas de procesamiento Ovito
        if '_surface_removal_ratio' in dataset.columns:
            avg_removal = dataset['_surface_removal_ratio'].mean()
            processing_msg = f"Features extraídas de interior (superficie removida: {avg_removal:.1%})"
        else:
            processing_msg = "Features extraídas (sin procesamiento Ovito)"
        
        # Reporte de progreso final
        if errors:
            self._report_progress(
                total_files, total_files,
                f"Completado con {len(errors)} errores: {total_features} {processing_msg}"
            )
            logger.warning(f"Se encontraron {len(errors)} errores durante el procesamiento")
        else:
            self._report_progress(
                total_files, total_files,
                f"Procesamiento completado: {total_features} {processing_msg}"
            )
        
        # Log estadísticas del target
        if 'vacancies' in dataset.columns:
            vac_stats = dataset['vacancies'].describe()
            logger.info(f"Distribución del target (vacancies reales): "
                       f"min={vac_stats['min']:.0f}, max={vac_stats['max']:.0f}, "
                       f"mean={vac_stats['mean']:.1f}")
    
    def _cleanup_temp_dir(self):
        """CORREGIDO: Limpiar directorio temporal de forma más robusta"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug(f"Directorio temporal limpiado: {self.temp_dir}")
                self.temp_dir = None
            except Exception as e:
                logger.warning(f"No se pudo limpiar directorio temporal {self.temp_dir}: {str(e)}")
    
    def _report_progress(self, current: int, total: int, message: str = ""):
        """Reportar progreso si hay callback"""
        if self.progress_callback:
            try:
                self.progress_callback(current, total, message)
            except Exception as e:
                logger.warning(f"Error en callback de progreso: {str(e)}")
    
    def stop_processing(self):
        """Solicitar detener el procesamiento"""
        self._stop_requested = True
        logger.info("Solicitud de detención recibida")
    
    def get_feature_summary(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Generar resumen detallado del dataset procesado con Ovito"""
        try:
            # Separar tipos de columnas
            feature_cols = [col for col in dataset.columns 
                           if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
            metadata_cols = [col for col in dataset.columns if col.startswith('_')]
            
            # Categorizar features
            categories = self._categorize_enhanced_features(feature_cols)
            
            # Análisis de calidad
            quality_metrics = self._analyze_data_quality(dataset, feature_cols)
            
            # Análisis específico de Ovito
            ovito_analysis = self._analyze_ovito_processing(dataset)
            
            summary = {
                "processing_info": {
                    "total_files": len(dataset),
                    "total_features": len(feature_cols),
                    "feature_mode": self.config.feature_mode.value,
                    "extractor_type": "EnhancedSafeFeatureExtractor_Ovito",
                    "ovito_pipeline": "ConstructSurface -> InvertSelection -> DeleteSelected",
                    "ovito_parameters": {
                        "surface_radius": self.surface_radius,
                        "smoothing_level": self.smoothing_level
                    },
                    "configuration": asdict(self.config)
                },
                "feature_categories": categories,
                "data_quality": quality_metrics,
                "ovito_processing": ovito_analysis,
                "target_info": self._analyze_target_info(dataset) if 'vacancies' in dataset.columns else None,
                "enhanced_features_summary": self.feature_extractor.get_feature_summary()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generando resumen: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_ovito_processing(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Analizar estadísticas del procesamiento Ovito"""
        analysis = {}
        
        try:
            if '_atoms_removed_surface' in dataset.columns:
                surface_removed = dataset['_atoms_removed_surface']
                removal_ratios = dataset['_surface_removal_ratio']
                
                analysis = {
                    "atoms_removed_stats": {
                        "mean": float(surface_removed.mean()),
                        "std": float(surface_removed.std()),
                        "min": int(surface_removed.min()),
                        "max": int(surface_removed.max())
                    },
                    "removal_ratio_stats": {
                        "mean": float(removal_ratios.mean()),
                        "std": float(removal_ratios.std()),
                        "min": float(removal_ratios.min()),
                        "max": float(removal_ratios.max())
                    }
                }
                
                if '_ovito_processing_success' in dataset.columns:
                    success_rate = dataset['_ovito_processing_success'].mean()
                    analysis["processing_success_rate"] = float(success_rate)
                else:
                    analysis["processing_success_rate"] = 1.0
            else:
                analysis["error"] = "No Ovito processing metadata found"
                
        except Exception as e:
            analysis["error"] = f"Error analyzing Ovito processing: {str(e)}"
        
        return analysis
    
    def _categorize_enhanced_features(self, feature_cols: List[str]) -> Dict[str, List[str]]:
        """Categorizar features mejoradas por tipo"""
        categories = {
            "energy_basic": [],
            "energy_advanced": [],
            "stress_basic": [],
            "stress_advanced": [],
            "coordination": [],
            "spatial_basic": [],
            "spatial_advanced": [],
            "voronoi": [],
            "combined_advanced": [],
            "ratios_advanced": [],
            "other": []
        }
        
        for col in feature_cols:
            col_lower = col.lower()
            
            if any(x in col_lower for x in ['pe_mean', 'pe_std', 'pe_median', 'pe_iqr', 'pe_mad', 'pe_entropy']):
                categories["energy_basic"].append(col)
            elif any(x in col_lower for x in ['pe_skew', 'pe_kurt', 'thermal_fluctuation', 'pe_disorder', 'pe_gradient', 'pe_variability']):
                categories["energy_advanced"].append(col)
            elif any(x in col_lower for x in ['stress_i1_mean', 'stress_i2_mean', 'stress_i3_mean', 'stress_vm_mean', 'stress_hydro_mean']):
                categories["stress_basic"].append(col)
            elif any(x in col_lower for x in ['stress_instability', 'stress_anisotropy', 'hydrostatic_pressure', 'stress_i1_i2', 'stress_i2_i3']):
                categories["stress_advanced"].append(col)
            elif 'coord' in col_lower:
                categories["coordination"].append(col)
            elif any(x in col_lower for x in ['spatial_std', 'gyration_radius']):
                categories["spatial_basic"].append(col)
            elif any(x in col_lower for x in ['spatial_anisotropy', 'atomic_density']):
                categories["spatial_advanced"].append(col)
            elif 'voro' in col_lower:
                categories["voronoi"].append(col)
            elif any(x in col_lower for x in ['energy_stress_coupling', 'structural_cohesion', 'thermodynamic_imbalance', 
                                            'vacancy_density_proxy', 'multiscale_disorder', 'energy_asymmetry']):
                categories["combined_advanced"].append(col)
            elif any(x in col_lower for x in ['spatial_energy_proxy', 'volume_energy_density', 'volume_packing']):
                categories["ratios_advanced"].append(col)
            else:
                categories["other"].append(col)
        
        return categories
    
    def _analyze_data_quality(self, dataset: pd.DataFrame, feature_cols: List[str]) -> Dict[str, Any]:
        """Analizar calidad de los datos"""
        try:
            null_counts = dataset[feature_cols].isnull().sum()
            inf_counts = dataset[feature_cols].apply(
                lambda x: np.isinf(x).sum() if x.dtype in [np.float64, np.int64] else 0
            )
            
            return {
                "completeness_ratio": float(1 - null_counts.sum() / (len(dataset) * len(feature_cols))) if len(feature_cols) > 0 else 1.0,
                "features_with_nulls": int((null_counts > 0).sum()),
                "features_with_inf": int((inf_counts > 0).sum()),
                "total_null_values": int(null_counts.sum())
            }
        except Exception as e:
            logger.error(f"Error en análisis de calidad: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_target_info(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Analizar información del target"""
        try:
            if 'vacancies' not in dataset.columns:
                return None
            
            target = dataset['vacancies']
            return {
                "min": int(target.min()),
                "max": int(target.max()),
                "mean": float(target.mean()),
                "std": float(target.std()),
                "median": float(target.median()),
                "unique_values": int(target.nunique())
            }
        except Exception as e:
            logger.error(f"Error en análisis de target: {str(e)}")
            return {"error": str(e)}
    
    def analyze_leakage(self, dataset: pd.DataFrame) -> str:
        """Realizar análisis completo de fuga y retornar reporte"""
        try:
            analysis = self.leakage_detector.detect_leakage(dataset)
            return self.leakage_detector.create_leakage_report(analysis)
        except Exception as e:
            logger.error(f"Error en análisis de fuga: {str(e)}")
            return f"Error en análisis de fuga: {str(e)}"