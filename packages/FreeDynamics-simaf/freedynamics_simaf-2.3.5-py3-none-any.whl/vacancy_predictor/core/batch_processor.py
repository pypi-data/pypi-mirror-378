"""
Procesador batch refactorizado - Clase principal que coordina todos los módulos
ACTUALIZADO para usar EnhancedSafeFeatureExtractor
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Callable
import logging
import threading
from dataclasses import asdict

# Importar módulos refactorizados
from .config import ProcessingConfig, FeatureMode
from .file_parser import LAMMPSFileParser
from .enhanced_safe_feature_extractor import EnhancedSafeFeatureExtractor  # ACTUALIZADO
from .data_leakage_detector import DataLeakageDetector

logger = logging.getLogger(__name__)


class BatchDumpProcessor:
    """
    Procesador batch refactorizado con separación de responsabilidades
    y control estricto de fuga de información.
    ACTUALIZADO para usar features mejoradas.
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        
        # Inicializar componentes especializados (ACTUALIZADO)
        self.file_parser = LAMMPSFileParser()
        #self.feature_extractor = EnhancedSafeFeatureExtractor(self.config)  # MEJORADO
        self.leakage_detector = DataLeakageDetector()
        
        # Callback para progreso
        self.progress_callback: Optional[Callable] = None
        
        # Estado del procesamiento
        self._stop_requested = False
    
    def set_parameters(self, **kwargs):
        """Actualizar parámetros de configuración"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Actualizado {key} = {value}")
        
        # Recrear feature extractor con nueva configuración (ACTUALIZADO)
        self.feature_extractor = EnhancedSafeFeatureExtractor(self.config)
    
    def set_feature_mode(self, mode: FeatureMode):
        """Establecer modo de extracción de features"""
        self.config.feature_mode = mode
        self.feature_extractor = EnhancedSafeFeatureExtractor(self.config)  # ACTUALIZADO
        logger.info(f"Modo de features establecido: {mode.value}")
    
    def set_progress_callback(self, callback: Callable):
        """Establecer callback para reportar progreso"""
        self.progress_callback = callback
    
    def process_directory(self, directory: str, 
                         validate_leakage: bool = True,
                         save_intermediate: bool = False) -> pd.DataFrame:
        """
        Procesar directorio completo con control de fuga
        
        Args:
            directory: Directorio con archivos .dump
            validate_leakage: Si validar fuga de información
            save_intermediate: Si guardar resultados intermedios
            
        Returns:
            DataFrame con features y target separados apropiadamente
        """
        self._stop_requested = False
        
        # Encontrar archivos dump
        dump_files = self.file_parser.find_dump_files(directory)
        
        if not dump_files:
            raise ValueError(f"No se encontraron archivos .dump en {directory}")
        
        logger.info(f"Encontrados {len(dump_files)} archivos .dump")
        logger.info(f"Modo: {self.config.feature_mode.value}")
        logger.info(f"Extractor: EnhancedSafeFeatureExtractor")  # NUEVO LOG
        
        self._report_progress(0, len(dump_files), "Iniciando procesamiento...")
        
        # Procesar archivos
        results = []
        errors = []
        
        for i, file_path in enumerate(dump_files, 1):
            if self._stop_requested:
                logger.info("Procesamiento detenido por usuario")
                break
            
            try:
                file_name = Path(file_path).name
                self._report_progress(i, len(dump_files), f"Procesando {file_name}")
                
                # Procesar archivo individual
                features = self._process_single_file(file_path)
                features["file"] = file_name
                features["file_path"] = file_path
                
                results.append(features)
                
                # Log sin revelar información sensible
                n_atoms = features.get('_n_atoms_metadata', 'N/A')
                n_features = len([k for k in features.keys() 
                                if not k.startswith('_') and k not in ['file', 'file_path', 'file_hash', 'vacancies']])
                logger.info(f"✓ {file_name}: {n_atoms} átomos, {n_features} features extraídas")
                
            except Exception as e:
                error_msg = f"Error en {Path(file_path).name}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        if not results:
            raise RuntimeError("No se pudieron procesar archivos correctamente")
        
        # Crear dataset
        dataset = pd.DataFrame(results).set_index("file").sort_index()
        
        # Log de summary de features mejoradas
        self._log_enhanced_features_summary(dataset)
        
        # Validar fuga de información si está habilitado
        if validate_leakage:
            self._validate_and_clean_dataset(dataset)
        
        # Guardar intermedios si está habilitado
        if save_intermediate:
            self._save_intermediate_results(dataset, directory)
        
        # Reporte final
        self._generate_final_report(dataset, errors)
        
        return dataset
    
    def _process_single_file(self, file_path: str) -> Dict[str, Any]:
        """Procesar un archivo individual"""
        # Parsear archivo
        df, n_atoms, metadata = self.file_parser.parse_last_frame(file_path)
        
        # Validar datos básicos
        if df.empty or n_atoms <= 0:
            raise ValueError(f"Datos inválidos: {n_atoms} átomos")
        
        # Extraer features (USANDO ENHANCED EXTRACTOR)
        features = self.feature_extractor.extract_features(df, n_atoms, metadata)
        
        # Agregar metadata de procesamiento
        features["_n_atoms_metadata"] = n_atoms
        features["_processing_mode"] = self.config.feature_mode.value
        features["_extractor_version"] = "EnhancedSafeFeatureExtractor"  # NUEVO
        
        return features
    
    def _log_enhanced_features_summary(self, dataset: pd.DataFrame):
        """Log del resumen de features mejoradas"""
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
        
        # Categorizar features
        original_features = []
        advanced_features = []
        
        for col in feature_cols:
            if any(col.startswith(prefix) for prefix in [
                'thermal_', 'pe_disorder_', 'pe_gradient_', 'stress_instability',
                'stress_anisotropy', 'hydrostatic_', 'atomic_density_',
                'spatial_anisotropy', 'volume_packing_', 'coordination_disorder',
                'effective_density_normalized', 'voro_vol_cv_enhanced',
                'energy_stress_', 'structural_cohesion', 'thermodynamic_imbalance',
                'vacancy_density_proxy', 'multiscale_disorder', 'energy_asymmetry',
                'pe_variability_', 'stress_I1_I2_', 'stress_I2_I3_',
                'spatial_energy_', 'volume_energy_', 'pe_skew_robust', 'pe_kurt_robust'
            ]):
                advanced_features.append(col)
            else:
                original_features.append(col)
        
        logger.info(f"FEATURES SUMMARY:")
        logger.info(f"  Original features: {len(original_features)}")
        logger.info(f"  Advanced features: {len(advanced_features)}")
        logger.info(f"  Total features: {len(feature_cols)}")
        
        if advanced_features:
            logger.info(f"  Advanced features incluyen: {advanced_features[:5]}")
    
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
            logger.warning(f"Patrones sospechosos detectados: {len(suspicious)}")
            for pattern in suspicious[:3]:
                logger.warning(f"  - {pattern}")
    
    def _save_intermediate_results(self, dataset: pd.DataFrame, directory: str):
        """Guardar resultados intermedios"""
        output_dir = Path(directory) / "processing_output"
        output_dir.mkdir(exist_ok=True)
        
        # Separar features de metadata
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash']]
        metadata_cols = [col for col in dataset.columns if col.startswith('_')]
        
        # Guardar features
        features_path = output_dir / "enhanced_features.csv"  # ACTUALIZADO NOMBRE
        dataset[feature_cols].to_csv(features_path)
        
        # Guardar metadata separadamente
        if metadata_cols:
            metadata_path = output_dir / "metadata.csv"
            dataset[metadata_cols].to_csv(metadata_path)
        
        # Guardar resumen de features mejoradas
        feature_summary = self.feature_extractor.get_feature_summary()
        summary_path = output_dir / "feature_summary.json"
        import json
        with open(summary_path, 'w') as f:
            json.dump(feature_summary, f, indent=2)
        
        # Guardar configuración
        config_path = output_dir / "processing_config.json"
        config_dict = asdict(self.config)
        config_dict['extractor_type'] = 'EnhancedSafeFeatureExtractor'  # NUEVO
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
        
        logger.info(f"Resultados intermedios guardados en {output_dir}")
    
    def _generate_final_report(self, dataset: pd.DataFrame, errors: List[str]):
        """Generar reporte final del procesamiento"""
        # Contar tipos de columnas
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
        
        total_files = len(dataset)
        total_features = len(feature_cols)
        
        # Reporte de progreso final
        if errors:
            self._report_progress(
                total_files, total_files,
                f"Completado con {len(errors)} errores: {total_features} features mejoradas extraídas"
            )
            logger.warning(f"Se encontraron {len(errors)} errores durante el procesamiento")
        else:
            self._report_progress(
                total_files, total_files,
                f"Procesamiento completado: {total_features} features mejoradas extraídas"
            )
        
        # Log estadísticas del target (si existe)
        if 'vacancies' in dataset.columns:
            vac_stats = dataset['vacancies'].describe()
            logger.info(f"Distribución del target (vacancies): "
                       f"min={vac_stats['min']:.0f}, max={vac_stats['max']:.0f}, "
                       f"mean={vac_stats['mean']:.1f}")
    
    def _report_progress(self, current: int, total: int, message: str = ""):
        """Reportar progreso si hay callback"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def stop_processing(self):
        """Solicitar detener el procesamiento"""
        self._stop_requested = True
        logger.info("Solicitud de detención recibida")
    
    def get_feature_summary(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Generar resumen detallado del dataset procesado"""
        # Separar tipos de columnas
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
        metadata_cols = [col for col in dataset.columns if col.startswith('_')]
        
        # Categorizar features (MEJORADO)
        categories = self._categorize_enhanced_features(feature_cols)
        
        # Análisis de calidad
        quality_metrics = self._analyze_data_quality(dataset, feature_cols)
        
        summary = {
            "processing_info": {
                "total_files": len(dataset),
                "total_features": len(feature_cols),
                "feature_mode": self.config.feature_mode.value,
                "extractor_type": "EnhancedSafeFeatureExtractor",  # NUEVO
                "configuration": asdict(self.config)
            },
            "feature_categories": categories,
            "data_quality": quality_metrics,
            "target_info": self._analyze_target_info(dataset) if 'vacancies' in dataset.columns else None,
            "enhanced_features_summary": self.feature_extractor.get_feature_summary()  # NUEVO
        }
        
        return summary
    
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
            
            # Energía básica vs avanzada
            if any(x in col_lower for x in ['pe_mean', 'pe_std', 'pe_median', 'pe_iqr', 'pe_mad', 'pe_entropy']):
                categories["energy_basic"].append(col)
            elif any(x in col_lower for x in ['pe_skew', 'pe_kurt', 'thermal_fluctuation', 'pe_disorder', 'pe_gradient', 'pe_variability']):
                categories["energy_advanced"].append(col)
            
            # Stress básico vs avanzado
            elif any(x in col_lower for x in ['stress_i1_mean', 'stress_i2_mean', 'stress_i3_mean', 'stress_vm_mean', 'stress_hydro_mean']):
                categories["stress_basic"].append(col)
            elif any(x in col_lower for x in ['stress_instability', 'stress_anisotropy', 'hydrostatic_pressure', 'stress_i1_i2', 'stress_i2_i3']):
                categories["stress_advanced"].append(col)
            
            # Coordinación
            elif 'coord' in col_lower:
                categories["coordination"].append(col)
            
            # Espaciales básicas vs avanzadas
            elif any(x in col_lower for x in ['spatial_std', 'gyration_radius']):
                categories["spatial_basic"].append(col)
            elif any(x in col_lower for x in ['spatial_anisotropy', 'atomic_density']):
                categories["spatial_advanced"].append(col)
            
            # Voronoi
            elif 'voro' in col_lower:
                categories["voronoi"].append(col)
            
            # Features combinadas avanzadas
            elif any(x in col_lower for x in ['energy_stress_coupling', 'structural_cohesion', 'thermodynamic_imbalance', 
                                            'vacancy_density_proxy', 'multiscale_disorder', 'energy_asymmetry']):
                categories["combined_advanced"].append(col)
            
            # Ratios avanzados
            elif any(x in col_lower for x in ['spatial_energy_proxy', 'volume_energy_density', 'volume_packing']):
                categories["ratios_advanced"].append(col)
            
            else:
                categories["other"].append(col)
        
        return categories
    
    def _analyze_data_quality(self, dataset: pd.DataFrame, feature_cols: List[str]) -> Dict[str, Any]:
        """Analizar calidad de los datos"""
        null_counts = dataset[feature_cols].isnull().sum()
        inf_counts = dataset[feature_cols].apply(
            lambda x: np.isinf(x).sum() if x.dtype in [np.float64, np.int64] else 0
        )
        
        return {
            "completeness_ratio": float(1 - null_counts.sum() / (len(dataset) * len(feature_cols))),
            "features_with_nulls": int((null_counts > 0).sum()),
            "features_with_inf": int((inf_counts > 0).sum()),
            "total_null_values": int(null_counts.sum())
        }
    
    def _analyze_target_info(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Analizar información del target"""
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
    
    def analyze_leakage(self, dataset: pd.DataFrame) -> str:
        """Realizar análisis completo de fuga y retornar reporte"""
        analysis = self.leakage_detector.detect_leakage(dataset)
        return self.leakage_detector.create_leakage_report(analysis)


# Funciones utilitarias para preparación de ML (SIN CAMBIOS)

def prepare_ml_dataset(dataset: pd.DataFrame,
                      target_col: str = 'vacancies',
                      remove_high_correlation: bool = True,
                      correlation_threshold: float = 0.9) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Preparar dataset para machine learning separando features del target
    
    IMPORTANTE: Esta función SEPARA correctamente features del target
    """
    if target_col not in dataset.columns:
        raise ValueError(f"Columna target '{target_col}' no encontrada")
    
    # Extraer target
    y = dataset[target_col].copy()
    
    # Identificar features (excluir target, metadata y auxiliares)
    exclude_cols = {target_col, 'file_path', 'file_hash'}
    exclude_cols.update([col for col in dataset.columns if col.startswith('_')])
    
    feature_cols = [col for col in dataset.columns if col not in exclude_cols]
    X = dataset[feature_cols].copy()
    
    # Eliminar features de alta correlación si está habilitado
    if remove_high_correlation:
        detector = DataLeakageDetector(correlation_threshold)
        
        # Crear dataset temporal para análisis
        temp_dataset = X.copy()
        temp_dataset[target_col] = y
        
        analysis = detector.detect_leakage(temp_dataset, target_col)
        
        if 'high_risk_features' in analysis:
            features_to_remove = [f['feature'] for f in analysis['high_risk_features']]
            if features_to_remove:
                X = X.drop(columns=features_to_remove, errors='ignore')
                logger.info(f"Eliminadas {len(features_to_remove)} features de alta correlación")
    
    # Imputar valores faltantes
    from sklearn.impute import SimpleImputer
    imputer = SimpleImputer(strategy='median')
    X_imputed = pd.DataFrame(
        imputer.fit_transform(X),
        columns=X.columns,
        index=X.index
    )
    
    logger.info(f"Dataset ML preparado: {X_imputed.shape[0]} muestras, "
               f"{X_imputed.shape[1]} features mejoradas, target: {target_col}")
    
    return X_imputed, y


def create_train_test_split(dataset: pd.DataFrame,
                           target_col: str = 'vacancies',
                           test_size: float = 0.2,
                           random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Crear división train/test con estratificación"""
    from sklearn.model_selection import train_test_split
    
    X, y = prepare_ml_dataset(dataset, target_col)
    
    # Estratificar por cuartiles del target si es continuo
    if y.nunique() > 10:
        stratify_bins = pd.qcut(y, q=4, labels=False, duplicates='drop')
    else:
        stratify_bins = y
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state,
        stratify=stratify_bins
    )
    
    logger.info(f"División creada: {len(X_train)} train, {len(X_test)} test con features mejoradas")
    
    return X_train, X_test, y_train, y_test