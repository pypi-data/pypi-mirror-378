"""
BatchProcessor Mejorado con capacidad de filtrado OVITO
Extiende el BatchProcessor existente para incluir filtrado de superficie
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Callable
import logging
import threading
from dataclasses import asdict, dataclass

# Importaciones de OVITO
from ovito.io import import_file, export_file
from ovito.modifiers import (
    ConstructSurfaceModifier,
    InvertSelectionModifier,
    DeleteSelectedModifier,
    AffineTransformationModifier
)

# Importar módulos existentes
from .config import ProcessingConfig, FeatureMode
from .file_parser import LAMMPSFileParser
from .feature_extractor import SafeFeatureExtractor
from .data_leakage_detector import DataLeakageDetector

logger = logging.getLogger(__name__)


@dataclass
class OvitoFilterConfig:
    """Configuración para filtrado OVITO"""
    enable_ovito_filter: bool = False
    surface_radius: float = 2.0
    smoothing_level: int = 0
    apply_stress_tensor: bool = False
    stress_tensor: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    export_filtered_dumps: bool = False
    filtered_dump_dir: Optional[str] = None


class BatchDumpProcessor:
    """
    BatchProcessor mejorado con capacidad de filtrado OVITO
    
    Combina el procesamiento batch existente con filtrado de superficie
    para calcular features solo en átomos alrededor del nanoporo
    """
    
    def __init__(self, 
                 config: Optional[ProcessingConfig] = None,
                 ovito_config: Optional[OvitoFilterConfig] = None):
        self.config = config or ProcessingConfig()
        self.ovito_config = ovito_config or OvitoFilterConfig()
        
        # Inicializar componentes especializados
        self.file_parser = LAMMPSFileParser()
        self.feature_extractor = SafeFeatureExtractor(self.config)
        self.leakage_detector = DataLeakageDetector()
        
        # Callback para progreso
        self.progress_callback: Optional[Callable] = None
        
        # Estado del procesamiento
        self._stop_requested = False
        
        # Crear directorio para dumps filtrados si es necesario
        if self.ovito_config.export_filtered_dumps and self.ovito_config.filtered_dump_dir:
            Path(self.ovito_config.filtered_dump_dir).mkdir(parents=True, exist_ok=True)
    
    def set_ovito_filter(self, 
                        enable: bool = True,
                        surface_radius: float = 3.0,
                        smoothing_level: int = 0,
                        apply_stress: bool = False,
                        stress_tensor: Tuple[float, float, float] = (1.0, 1.0, 1.0)):
        """Configurar filtrado OVITO"""
        self.ovito_config.enable_ovito_filter = enable
        self.ovito_config.surface_radius = surface_radius
        self.ovito_config.smoothing_level = smoothing_level
        self.ovito_config.apply_stress_tensor = apply_stress
        self.ovito_config.stress_tensor = stress_tensor
        
        logger.info(f"Filtrado OVITO {'habilitado' if enable else 'deshabilitado'}")
        if enable:
            logger.info(f"  - Radio superficie: {surface_radius}")
            logger.info(f"  - Nivel suavizado: {smoothing_level}")
            logger.info(f"  - Tensor stress: {apply_stress}")
    
    def set_parameters(self, **kwargs):
        """Actualizar parámetros de configuración"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Actualizado {key} = {value}")
        
        # Recrear feature extractor con nueva configuración
        self.feature_extractor = SafeFeatureExtractor(self.config)
    
    def set_feature_mode(self, mode: FeatureMode):
        """Establecer modo de extracción de features"""
        self.config.feature_mode = mode
        self.feature_extractor = SafeFeatureExtractor(self.config)
        logger.info(f"Modo de features establecido: {mode.value}")
    
    def set_progress_callback(self, callback: Callable):
        """Establecer callback para reportar progreso"""
        self.progress_callback = callback
    
    def process_directory(self, directory: str, 
                         validate_leakage: bool = True,
                         save_intermediate: bool = False) -> pd.DataFrame:
        """
        Procesar directorio completo con filtrado OVITO opcional
        
        Args:
            directory: Directorio con archivos .dump
            validate_leakage: Si validar contra fuga de información
            save_intermediate: Si guardar resultados intermedios
            
        Returns:
            DataFrame con features extraídas
        """
        logger.info(f"Iniciando procesamiento de directorio: {directory}")
        
        if self.ovito_config.enable_ovito_filter:
            logger.info("MODO OVITO HABILITADO - Features calculadas solo en región nanoporo")
            logger.info(f"Radio superficie: {self.ovito_config.surface_radius}")
            logger.info(f"Nivel suavizado: {self.ovito_config.smoothing_level}")
        else:
            logger.info("MODO ESTÁNDAR - Features calculadas en todos los átomos")
        
        # Encontrar archivos
        dump_files = self.find_dump_files(directory)
        if not dump_files:
            raise ValueError(f"No se encontraron archivos .dump en {directory}")
        
        logger.info(f"Encontrados {len(dump_files)} archivos para procesar")
        
        # Procesar archivos
        results = []
        errors = []
        filter_stats = []  # Estadísticas del filtrado OVITO
        
        for i, file_path in enumerate(dump_files):
            if self._stop_requested:
                logger.info("Procesamiento detenido por solicitud del usuario")
                break
                
            try:
                # Reportar progreso
                if self.progress_callback:
                    self.progress_callback(i, len(dump_files), f"Procesando {Path(file_path).name}")
                
                # Procesar archivo individual (con o sin OVITO)
                if self.ovito_config.enable_ovito_filter:
                    features, stats = self._process_single_file_with_ovito(file_path)
                    filter_stats.append(stats)
                else:
                    features = self._process_single_file_standard(file_path)
                
                results.append(features)
                
                logger.debug(f"Procesado {Path(file_path).name}: {len(features)} features")
                
            except Exception as e:
                error_msg = f"Error procesando {file_path}: {str(e)}"
                logger.error(error_msg)
                errors.append({"file": file_path, "error": str(e)})
        
        # Crear dataset
        if not results:
            raise RuntimeError("No se pudieron procesar archivos válidos")
        
        dataset = pd.DataFrame(results)
        logger.info(f"Dataset creado: {len(dataset)} filas, {len(dataset.columns)} columnas")
        
        # Agregar estadísticas de filtrado si se usó OVITO
        if self.ovito_config.enable_ovito_filter and filter_stats:
            self._add_filter_statistics_to_report(filter_stats)
        
        # Validar contra fuga de información
        if validate_leakage:
            self._validate_and_clean_dataset(dataset)
        
        # Reportar resultados finales
        if self.progress_callback:
            self.progress_callback(len(dump_files), len(dump_files), "Completado")
        
        # Generar reporte
        self._generate_final_report(dataset, errors, filter_stats if self.ovito_config.enable_ovito_filter else None)
        
        return dataset
    
    def _process_single_file_standard(self, file_path: str) -> Dict[str, Any]:
        """
        Procesar archivo sin filtrado OVITO (método original)
        """
        # Parsear archivo
        df, n_atoms, metadata = self.file_parser.parse_last_frame(file_path)
        
        # Validar datos básicos
        if df.empty or n_atoms <= 0:
            raise ValueError(f"Datos inválidos: {n_atoms} átomos")
        
        # Extraer features
        features = self.feature_extractor.extract_features(df, metadata)
        
        # Agregar metadata de procesamiento
        features["_n_atoms_in_file"] = n_atoms
        features["_processing_mode"] = f"{self.config.feature_mode.value}_standard"
        features["_file_path"] = file_path
        features["_ovito_filtered"] = False
        
        # Verificar cálculo de vacancies
        calculated_vacancies = self.config.atm_total - n_atoms
        if features.get("vacancies") != calculated_vacancies:
            logger.warning(f"Inconsistencia en cálculo de vacancies: "
                         f"esperado {calculated_vacancies}, obtenido {features.get('vacancies')}")
        
        return features
    
    def _process_single_file_with_ovito(self, file_path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Procesar archivo CON filtrado OVITO
        
        Returns:
            Tuple de (features, estadísticas_filtrado)
        """
        logger.debug(f"Aplicando filtrado OVITO a {Path(file_path).name}")
        
        # 1. Cargar archivo y obtener número de átomos original
        pipeline = import_file(file_path)
        original_data = pipeline.compute()
        n_atoms_original = original_data.particles.count
        
        # 2. Aplicar deformación afín si se solicita
        if self.ovito_config.apply_stress_tensor:
            pipeline.modifiers.append(AffineTransformationModifier(
                operate_on={'particles', 'cell'},
                transformation=[
                    [self.ovito_config.stress_tensor[0], 0, 0, 0],
                    [0, self.ovito_config.stress_tensor[1], 0, 0],
                    [0, 0, self.ovito_config.stress_tensor[2], 0]
                ]
            ))
        
        # 3. Aplicar filtro de superficie
        pipeline.modifiers.append(ConstructSurfaceModifier(
            radius=self.ovito_config.surface_radius,
            smoothing_level=self.ovito_config.smoothing_level,
            identify_regions=True,
            select_surface_particles=True
        ))
        
        # 4. Invertir selección para quedarse con región nanoporo
        pipeline.modifiers.append(InvertSelectionModifier())
        
        # 5. Eliminar átomos seleccionados (superficie)
        pipeline.modifiers.append(DeleteSelectedModifier())
        
        # 6. Obtener datos filtrados
        filtered_data = pipeline.compute()
        n_atoms_filtered = filtered_data.particles.count
        
        # 7. Estadísticas del filtrado
        filter_ratio = n_atoms_filtered / n_atoms_original if n_atoms_original > 0 else 0
        filter_stats = {
            'file': Path(file_path).name,
            'n_atoms_original': n_atoms_original,
            'n_atoms_filtered': n_atoms_filtered,
            'filter_ratio': filter_ratio,
            'atoms_removed': n_atoms_original - n_atoms_filtered
        }
        
        logger.debug(f"Filtrado OVITO: {n_atoms_original} → {n_atoms_filtered} átomos (ratio: {filter_ratio:.3f})")
        
        # 8. Exportar dump filtrado si se solicita
        if self.ovito_config.export_filtered_dumps and self.ovito_config.filtered_dump_dir:
            filtered_dump_path = Path(self.ovito_config.filtered_dump_dir) / f"filtered_{Path(file_path).stem}.dump"
            try:
                export_file(
                    pipeline,
                    str(filtered_dump_path),
                    "lammps/dump",
                    columns=[
                        "Particle Identifier",
                        "Particle Type",
                        "Position.X",
                        "Position.Y",
                        "Position.Z"
                    ]
                )
            except Exception as e:
                logger.warning(f"No se pudo exportar dump filtrado: {e}")
        
        # 9. Convertir datos filtrados a DataFrame
        df_filtered = self._ovito_data_to_dataframe(filtered_data)
        
        # 10. Crear metadata para extracción de features
        metadata = {
            'n_atoms_original': n_atoms_original,
            'n_atoms_filtered': n_atoms_filtered,
            'filter_ratio': filter_ratio,
            'file_path': file_path
        }
        
        # 11. Extraer features de los datos filtrados
        features = self.feature_extractor.extract_features(df_filtered, metadata)
        
        # 12. Agregar metadata específico de OVITO
        features["_n_atoms_original"] = n_atoms_original
        features["_n_atoms_filtered"] = n_atoms_filtered
        features["_filter_ratio"] = filter_ratio
        features["_atoms_removed"] = n_atoms_original - n_atoms_filtered
        features["_processing_mode"] = f"{self.config.feature_mode.value}_ovito_filtered"
        features["_file_path"] = file_path
        features["_ovito_filtered"] = True
        features["_surface_radius"] = self.ovito_config.surface_radius
        features["_smoothing_level"] = self.ovito_config.smoothing_level
        
        # 13. Calcular vacancies basado en átomos ORIGINALES (no filtrados)
        calculated_vacancies = self.config.atm_total - n_atoms_original
        features["vacancies"] = calculated_vacancies
        
        # 14. Limpiar pipeline
        pipeline.modifiers.clear()
        
        return features, filter_stats
    
    def _ovito_data_to_dataframe(self, data) -> pd.DataFrame:
        """Convertir datos de OVITO a DataFrame de pandas"""
        df_dict = {}
        
        # Posiciones
        positions = data.particles.positions
        df_dict['x'] = positions[:, 0]
        df_dict['y'] = positions[:, 1] 
        df_dict['z'] = positions[:, 2]
        
        # Otras propiedades disponibles
        for prop_name in data.particles.keys():
            try:
                prop_data = data.particles[prop_name]
                if len(prop_data.shape) == 1:  # Propiedades escalares
                    df_dict[prop_name] = prop_data[:]
                elif len(prop_data.shape) == 2 and prop_data.shape[1] <= 6:  # Tensores pequeños
                    for i in range(prop_data.shape[1]):
                        df_dict[f"{prop_name}[{i+1}]"] = prop_data[:, i]
            except Exception as e:
                logger.debug(f"No se pudo extraer propiedad {prop_name}: {e}")
        
        return pd.DataFrame(df_dict)
    
    def _add_filter_statistics_to_report(self, filter_stats: List[Dict[str, Any]]):
        """Agregar estadísticas del filtrado OVITO al reporte"""
        if not filter_stats:
            return
        
        df_stats = pd.DataFrame(filter_stats)
        
        logger.info("ESTADÍSTICAS DEL FILTRADO OVITO:")
        logger.info(f"  - Ratio promedio de filtrado: {df_stats['filter_ratio'].mean():.3f}")
        logger.info(f"  - Ratio mínimo: {df_stats['filter_ratio'].min():.3f}")
        logger.info(f"  - Ratio máximo: {df_stats['filter_ratio'].max():.3f}")
        logger.info(f"  - Átomos promedio removidos: {df_stats['atoms_removed'].mean():.0f}")
        logger.info(f"  - Átomos promedio restantes: {df_stats['n_atoms_filtered'].mean():.0f}")
    
    def _validate_and_clean_dataset(self, dataset: pd.DataFrame):
        """Validar y limpiar dataset para evitar fuga"""
        logger.info("Validando dataset contra fuga de información...")
        
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
            for feature_info in high_risk_features[:5]:  # Log primeras 5
                logger.warning(f"  - {feature_info['feature']}: r={feature_info['correlation']:.3f}")
            
            # Eliminar del dataset
            dataset.drop(columns=features_to_remove, inplace=True, errors='ignore')
        
        # Eliminar features prohibidas explícitamente
        forbidden_found = [col for col in self.config.forbidden_features 
                          if col in dataset.columns]
        if forbidden_found:
            dataset.drop(columns=forbidden_found, inplace=True)
            logger.info(f"Eliminadas features prohibidas: {forbidden_found}")
        
        # Log resultados de validación
        suspicious = leakage_analysis['suspicious_features']
        if suspicious:
            logger.warning(f"Patrones sospechosos detectados en {len(suspicious)} features")
            logger.warning("Considera revisar estas features manualmente")
        
        # Log features finales
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['vacancies', 'file_hash']]
        logger.info(f"Features finales para ML: {len(feature_cols)}")
    
    def _generate_final_report(self, dataset: pd.DataFrame, errors: List[Dict], filter_stats: Optional[List[Dict]] = None):
        """Generar reporte final del procesamiento"""
        logger.info("=" * 50)
        logger.info("REPORTE FINAL DE PROCESAMIENTO MEJORADO")
        logger.info("=" * 50)
        
        # Modo de procesamiento
        if self.ovito_config.enable_ovito_filter:
            logger.info("MODO: OVITO FILTRADO (features calculadas solo en región nanoporo)")
        else:
            logger.info("MODO: ESTÁNDAR (features calculadas en todos los átomos)")
        
        # Estadísticas generales
        logger.info(f"Archivos procesados exitosamente: {len(dataset)}")
        logger.info(f"Errores encontrados: {len(errors)}")
        
        if errors:
            logger.warning("Archivos con errores:")
            for error in errors[:5]:  # Mostrar máximo 5 errores
                logger.warning(f"  - {Path(error['file']).name}: {error['error']}")
        
        # Estadísticas del dataset
        if len(dataset) > 0:
            # Columnas por tipo
            feature_cols = [col for col in dataset.columns 
                           if not col.startswith('_') and col not in ['vacancies', 'file_hash']]
            metadata_cols = [col for col in dataset.columns if col.startswith('_')]
            
            logger.info(f"Features extraídas: {len(feature_cols)}")
            logger.info(f"Columnas de metadata: {len(metadata_cols)}")
            
            # Estadísticas de vacancies
            if 'vacancies' in dataset.columns:
                vac_stats = dataset['vacancies'].describe()
                logger.info(f"Rango de vacancies: {vac_stats['min']:.0f} - {vac_stats['max']:.0f}")
                logger.info(f"Media de vacancies: {vac_stats['mean']:.2f}")
                logger.info(f"Desviación estándar de vacancies: {vac_stats['std']:.2f}")
            
            # Estadísticas específicas de OVITO
            if filter_stats:
                df_filter = pd.DataFrame(filter_stats)
                logger.info("ESTADÍSTICAS DE FILTRADO OVITO:")
                logger.info(f"  - Ratio promedio de átomos conservados: {df_filter['filter_ratio'].mean():.3f}")
                logger.info(f"  - Átomos promedio por archivo (post-filtro): {df_filter['n_atoms_filtered'].mean():.0f}")
                logger.info(f"  - Átomos promedio removidos: {df_filter['atoms_removed'].mean():.0f}")
            
            # Verificar calidad de features
            null_counts = dataset[feature_cols].isnull().sum()
            features_with_nulls = null_counts[null_counts > 0]
            
            if len(features_with_nulls) > 0:
                logger.warning(f"Features con valores nulos: {len(features_with_nulls)}")
                for feature, null_count in features_with_nulls.head().items():
                    logger.warning(f"  - {feature}: {null_count} nulos")
            else:
                logger.info("✓ No se encontraron valores nulos en features")
            
            # Verificar varianza
            numeric_features = dataset[feature_cols].select_dtypes(include=[np.number])
            zero_var_features = numeric_features.columns[numeric_features.var() == 0]
            
            if len(zero_var_features) > 0:
                logger.warning(f"Features con varianza cero: {len(zero_var_features)}")
                logger.warning("Considera eliminar estas features antes del entrenamiento")
            else:
                logger.info("✓ Todas las features tienen varianza positiva")
        
        logger.info("=" * 50)
    
    def find_dump_files(self, directory: str) -> List[str]:
        """Encontrar todos los archivos .dump en un directorio"""
        directory_path = Path(directory)
        dump_files = []
        
        # Patrones de búsqueda
        patterns = ["*.dump", "*.dump.gz", "dump.*", "dump.*.gz"]
        
        for pattern in patterns:
            dump_files.extend(directory_path.glob(pattern))
        
        return sorted([str(f) for f in dump_files])
    
    def stop_processing(self):
        """Detener el procesamiento"""
        self._stop_requested = True
        logger.info("Solicitud de parada recibida")
    
    def reset_stop_flag(self):
        """Resetear flag de parada"""
        self._stop_requested = False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Obtener resumen de la configuración actual"""
        summary = {
            "atm_total": self.config.atm_total,
            "energy_range": (self.config.energy_min, self.config.energy_max),
            "energy_bins": self.config.energy_bins,
            "feature_mode": self.config.feature_mode.value,
            "add_noise": self.config.add_noise,
            "noise_level": self.config.noise_level if self.config.add_noise else None,
            "forbidden_features": list(self.config.forbidden_features),
            "validate_features": self.config.validate_features,
            # Configuración OVITO
            "ovito_filter_enabled": self.ovito_config.enable_ovito_filter,
            "surface_radius": self.ovito_config.surface_radius,
            "smoothing_level": self.ovito_config.smoothing_level,
            "apply_stress_tensor": self.ovito_config.apply_stress_tensor,
            "stress_tensor": self.ovito_config.stress_tensor
        }
        return summary
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validar configuración antes del procesamiento"""
        issues = []
        warnings = []
        
        # Validar parámetros básicos
        if self.config.atm_total <= 0:
            issues.append("atm_total debe ser positivo")
        
        if self.config.energy_min >= self.config.energy_max:
            issues.append("energy_min debe ser menor que energy_max")
        
        if self.config.energy_bins <= 0:
            issues.append("energy_bins debe ser positivo")
        
        # Validar configuración OVITO
        if self.ovito_config.enable_ovito_filter:
            if self.ovito_config.surface_radius <= 0:
                issues.append("surface_radius debe ser positivo cuando OVITO está habilitado")
            
            if self.ovito_config.smoothing_level < 0:
                warnings.append("smoothing_level negativo puede causar problemas")
        
        # Validar configuración de ruido
        if self.config.add_noise and self.config.noise_level <= 0:
            warnings.append("add_noise está activado pero noise_level no es positivo")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }


# Funciones auxiliares para crear procesadores preconfigurados
def create_standard_processor(atm_total: int = 16384,
                            energy_min: float = -4.0,
                            energy_max: float = -3.0,
                            energy_bins: int = 10,
                            feature_mode: FeatureMode = FeatureMode.STANDARD) -> BatchDumpProcessor:
    """Crear procesador estándar sin filtrado OVITO"""
    config = ProcessingConfig(
        atm_total=atm_total,
        energy_min=energy_min,
        energy_max=energy_max,
        energy_bins=energy_bins,
        feature_mode=feature_mode,
        add_noise=False,
        validate_features=True
    )
    
    ovito_config = OvitoFilterConfig(enable_ovito_filter=False)
    
    return BatchDumpProcessor(config, ovito_config)


def create_ovito_processor(atm_total: int = 16384,
                          surface_radius: float = 3.0,
                          smoothing_level: int = 0,
                          energy_min: float = -4.0,
                          energy_max: float = -3.0,
                          energy_bins: int = 10,
                          apply_stress: bool = False,
                          stress_tensor: Tuple[float, float, float] = (1.0, 1.0, 1.0),
                          feature_mode: FeatureMode = FeatureMode.STANDARD) -> BatchDumpProcessor:
    """Crear procesador con filtrado OVITO habilitado"""
    config = ProcessingConfig(
        atm_total=atm_total,
        energy_min=energy_min,
        energy_max=energy_max,
        energy_bins=energy_bins,
        feature_mode=feature_mode,
        add_noise=False,
        validate_features=True
    )
    
    ovito_config = OvitoFilterConfig(
        enable_ovito_filter=True,
        surface_radius=surface_radius,
        smoothing_level=smoothing_level,
        apply_stress_tensor=apply_stress,
        stress_tensor=stress_tensor,
        export_filtered_dumps=False
    )
    
    return BatchDumpProcessor(config, ovito_config)