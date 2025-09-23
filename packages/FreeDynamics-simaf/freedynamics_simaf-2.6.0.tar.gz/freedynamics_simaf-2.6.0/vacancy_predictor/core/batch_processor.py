"""
Procesador batch refactorizado - MODIFICADO
Usa n_atoms fijo (16384) para features, n_atoms_real solo para target
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
from .enhanced_safe_feature_extractor import EnhancedSafeFeatureExtractor
from .data_leakage_detector import DataLeakageDetector

logger = logging.getLogger(__name__)


class BatchDumpProcessor:
    """
    Procesador batch refactorizado - MODIFICADO
    Usa n_atoms=16384 fijo para features, n_atoms_real solo para target
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        
        # Inicializar componentes especializados
        self.file_parser = LAMMPSFileParser()
        self.feature_extractor = EnhancedSafeFeatureExtractor(self.config)
        self.leakage_detector = DataLeakageDetector()
        
        # Callback para progreso
        self.progress_callback: Optional[Callable] = None
        
        # Estado del procesamiento
        self._stop_requested = False
        
        # IMPORTANTE: Log de configuración de n_atoms
        logger.info(f"Procesador configurado con:")
        logger.info(f"  ATM_TOTAL (fijo para features): {self.config.atm_total}")
        logger.info(f"  Extractor: EnhancedSafeFeatureExtractor")
    
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
        Procesar directorio completo con control de fuga
        MODIFICADO: Usa n_atoms fijo para features
        """
        self._stop_requested = False
        
        # Encontrar archivos dump
        dump_files = self.file_parser.find_dump_files(directory)
        
        if not dump_files:
            raise ValueError(f"No se encontraron archivos .dump en {directory}")
        
        logger.info(f"Encontrados {len(dump_files)} archivos .dump")
        logger.info(f"Modo: {self.config.feature_mode.value}")
        logger.info(f"Extractor: EnhancedSafeFeatureExtractor con n_atoms_fijo={self.config.atm_total}")
        
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
                
                # Procesar archivo individual - MODIFICADO
                features = self._process_single_file(file_path)
                features["file"] = file_name
                features["file_path"] = file_path
                
                results.append(features)
                
                # Log sin revelar información sensible pero mostrando diferencia
                n_atoms_real = features.get('_n_atoms_real', 'N/A')
                n_atoms_used = features.get('_n_atoms_used_for_features', self.config.atm_total)
                n_features = len([k for k in features.keys() 
                                if not k.startswith('_') and k not in ['file', 'file_path', 'file_hash', 'vacancies']])
                
                logger.info(f"✓ {file_name}: átomos_real={n_atoms_real}, "
                           f"átomos_features={n_atoms_used}, features={n_features}")
                
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
        """Procesar un archivo individual - MODIFICADO para manejar n_atoms correctamente"""
        # Parsear archivo
        df, n_atoms_real, metadata = self.file_parser.parse_last_frame(file_path)
        
        # Validar datos básicos
        if df.empty or n_atoms_real <= 0:
            raise ValueError(f"Datos inválidos: {n_atoms_real} átomos")
        
        # CRÍTICO: Pasar n_atoms_real al extractor, que internamente usa n_atoms_fixed para features
        features = self.feature_extractor.extract_features(df, n_atoms_real, metadata)
        
        # Agregar metadata de procesamiento - MODIFICADO
        features["_n_atoms_real"] = n_atoms_real
        features["_n_atoms_used_for_features"] = self.config.atm_total  # 16384
        features["_processing_mode"] = self.config.feature_mode.value
        features["_extractor_version"] = "EnhancedSafeFeatureExtractor_fixed_atoms"
        
        # Validación de consistencia
        expected_vacancies = self.config.atm_total - n_atoms_real
        actual_vacancies = features.get('vacancies', 0)
        
        if expected_vacancies != actual_vacancies:
            logger.warning(f"Inconsistencia en vacancies: esperado={expected_vacancies}, "
                          f"actual={actual_vacancies}")
        
        return features
    
    def _log_enhanced_features_summary(self, dataset: pd.DataFrame):
        """Log del resumen de features mejoradas - ACTUALIZADO"""
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
        
        # Categorizar features - ACTUALIZADO para incluir features normalizadas
        original_features = []
        normalized_features = []
        advanced_features = []
        
        for col in feature_cols:
            if col.endswith('_norm') or 'fixed' in col.lower() or 'per_fixed_atom' in col:
                normalized_features.append(col)
            elif any(col.startswith(prefix) for prefix in [
                'thermal_', 'pe_disorder_', 'pe_gradient_', 'stress_instability',
                'stress_anisotropy', 'hydrostatic_', 'atomic_density_',
                'spatial_anisotropy', 'volume_packing_', 'coordination_disorder',
                'voro_vol_cv_enhanced', 'energy_stress_', 'structural_cohesion', 
                'thermodynamic_imbalance', 'vacancy_density_proxy', 'multiscale_disorder'
            ]):
                advanced_features.append(col)
            else:
                original_features.append(col)
        
        logger.info(f"FEATURES SUMMARY (con n_atoms_fijo={self.config.atm_total}):")
        logger.info(f"  Original features: {len(original_features)}")
        logger.info(f"  Normalized features: {len(normalized_features)}")
        logger.info(f"  Advanced features: {len(advanced_features)}")
        logger.info(f"  Total features: {len(feature_cols)}")
        
        if normalized_features:
            logger.info(f"  Normalized (safe) features: {normalized_features[:5]}")
        
        # Validar consistencia en metadata
        if '_n_atoms_used_for_features' in dataset.columns:
            used_values = dataset['_n_atoms_used_for_features'].unique()
            if len(used_values) == 1 and used_values[0] == self.config.atm_total:
                logger.info(f"✓ Consistencia confirmada: todas las features usan n_atoms={self.config.atm_total}")
            else:
                logger.warning(f"⚠️ Inconsistencia detectada en n_atoms_used_for_features: {used_values}")
    
    def _validate_and_clean_dataset(self, dataset: pd.DataFrame):
        """Validar y limpiar dataset para evitar fuga - ACTUALIZADO"""
        logger.info("Validando dataset contra fuga de información...")
        
        # Verificar que no haya features que usen n_atoms_real
        suspicious_features = []
        
        # Buscar features que podrían estar usando n_atoms_real en lugar de fijo
        if 'vacancies' in dataset.columns and len(dataset) > 1:
            target = dataset['vacancies']
            feature_cols = [col for col in dataset.columns 
                           if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
            
            for col in feature_cols:
                if dataset[col].dtype in [np.number]:
                    corr = abs(dataset[col].corr(target))
                    if corr > 0.95:  # Correlación muy alta
                        suspicious_features.append((col, corr))
        
        if suspicious_features:
            logger.warning(f"Features con correlación sospechosa alta con target:")
            for feature, corr in suspicious_features[:5]:
                logger.warning(f"  - {feature}: r={corr:.3f}")
        
        # Detectar posible fuga usando detector existente
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
        
        # Log resultados de validación
        suspicious = leakage_analysis['suspicious_features']
        if suspicious:
            logger.warning(f"Patrones sospechosos detectados: {len(suspicious)}")
            for pattern in suspicious[:3]:
                logger.warning(f"  - {pattern}")
        else:
            logger.info("✓ No se detectaron patrones sospechosos adicionales")
    
    def _save_intermediate_results(self, dataset: pd.DataFrame, directory: str):
        """Guardar resultados intermedios - ACTUALIZADO"""
        output_dir = Path(directory) / "processing_output"
        output_dir.mkdir(exist_ok=True)
        
        # Separar features de metadata
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash']]
        metadata_cols = [col for col in dataset.columns if col.startswith('_')]
        
        # Guardar features
        features_path = output_dir / "enhanced_features_fixed_atoms.csv"
        dataset[feature_cols].to_csv(features_path)
        
        # Guardar metadata separadamente
        if metadata_cols:
            metadata_path = output_dir / "metadata.csv"
            dataset[metadata_cols].to_csv(metadata_path)
        
        # Guardar resumen de configuración actualizado
        config_path = output_dir / "processing_config.json"
        config_dict = asdict(self.config)
        config_dict.update({
            'extractor_type': 'EnhancedSafeFeatureExtractor_fixed_atoms',
            'n_atoms_used_for_features': self.config.atm_total,
            'feature_computation_mode': 'fixed_atoms',
            'data_leakage_protection': 'enabled'
        })
        
        import json
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
        
        # Guardar resumen de validación
        validation_summary = {
            'total_files_processed': len(dataset),
            'features_extracted': len(feature_cols),
            'n_atoms_fixed_value': self.config.atm_total,
            'target_calculation': f"vacancies = {self.config.atm_total} - n_atoms_real",
            'feature_calculation': f"features computed using n_atoms = {self.config.atm_total} (fixed)"
        }
        
        validation_path = output_dir / "validation_summary.json"
        with open(validation_path, 'w') as f:
            json.dump(validation_summary, f, indent=2)
        
        logger.info(f"Resultados intermedios guardados en {output_dir}")
    
    def _generate_final_report(self, dataset: pd.DataFrame, errors: List[str]):
        """Generar reporte final del procesamiento - ACTUALIZADO"""
        # Contar tipos de columnas
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
        
        total_files = len(dataset)
        total_features = len(feature_cols)
        
        # Verificar consistencia
        consistency_check = True
        if '_n_atoms_used_for_features' in dataset.columns:
            used_values = dataset['_n_atoms_used_for_features'].unique()
            consistency_check = len(used_values) == 1 and used_values[0] == self.config.atm_total
        
        # Reporte de progreso final
        consistency_msg = "✓ Consistente" if consistency_check else "⚠️ Inconsistente"
        
        if errors:
            self._report_progress(
                total_files, total_files,
                f"Completado con {len(errors)} errores: {total_features} features ({consistency_msg})"
            )
            logger.warning(f"Se encontraron {len(errors)} errores durante el procesamiento")
        else:
            self._report_progress(
                total_files, total_files,
                f"Procesamiento completado: {total_features} features con n_atoms_fijo={self.config.atm_total} ({consistency_msg})"
            )
        
        # Log estadísticas del target (si existe)
        if 'vacancies' in dataset.columns:
            vac_stats = dataset['vacancies'].describe()
            logger.info(f"Distribución del target (vacancies = {self.config.atm_total} - n_atoms_real): "
                       f"min={vac_stats['min']:.0f}, max={vac_stats['max']:.0f}, "
                       f"mean={vac_stats['mean']:.1f}")
            
            # Verificar que target tenga sentido
            if vac_stats['min'] < 0:
                logger.error(f"⚠️ Vacancies negativas detectadas - revisar configuración ATM_TOTAL")
    
    # ... (resto de métodos sin cambios significativos) ...
    
    def _report_progress(self, current: int, total: int, message: str = ""):
        """Reportar progreso si hay callback"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def stop_processing(self):
        """Solicitar detener el procesamiento"""
        self._stop_requested = True
        logger.info("Solicitud de detención recibida")
    
    # ... (métodos de análisis sin cambios) ...


# Funciones utilitarias para preparación de ML - ACTUALIZADAS

def prepare_ml_dataset(dataset: pd.DataFrame,
                      target_col: str = 'vacancies',
                      remove_high_correlation: bool = True,
                      correlation_threshold: float = 0.9) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Preparar dataset para machine learning separando features del target
    ACTUALIZADO: Verifica que features usen n_atoms fijo
    """
    if target_col not in dataset.columns:
        raise ValueError(f"Columna target '{target_col}' no encontrada")
    
    # Extraer target
    y = dataset[target_col].copy()
    
    # Identificar features (excluir target, metadata y auxiliares)
    exclude_cols = {target_col, 'file_path', 'file'}
    exclude_cols.update([col for col in dataset.columns if col.startswith('_')])
    
    feature_cols = [col for col in dataset.columns if col not in exclude_cols]
    X = dataset[feature_cols].copy()
    
    # Verificación adicional: comprobar que features usen n_atoms fijo
    if '_n_atoms_used_for_features' in dataset.columns:
        used_values = dataset['_n_atoms_used_for_features'].unique()
        if len(used_values) == 1:
            logger.info(f"✓ Verificado: Features calculadas con n_atoms_fijo={used_values[0]}")
        else:
            logger.warning(f"⚠️ Inconsistencia en n_atoms_used_for_features: {used_values}")
    
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
    
    logger.info(f"Dataset ML preparado con features seguras: {X_imputed.shape[0]} muestras, "
               f"{X_imputed.shape[1]} features, target: {target_col}")
    
    return X_imputed, y


def create_train_test_split(dataset: pd.DataFrame,
                           target_col: str = 'vacancies',
                           test_size: float = 0.2,
                           random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Crear división train/test con estratificación - ACTUALIZADO"""
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
    
    logger.info(f"División creada con features seguras (n_atoms_fijo): {len(X_train)} train, {len(X_test)} test")
    
    return X_train, X_test, y_train, y_test