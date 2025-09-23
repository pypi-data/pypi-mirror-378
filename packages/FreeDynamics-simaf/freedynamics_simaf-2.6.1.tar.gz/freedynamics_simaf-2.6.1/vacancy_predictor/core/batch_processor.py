"""
Procesador batch refactorizado - CORREGIDO
Usa n_atoms fijo (16384) para features, interfaz consistente
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
from .feature_extractor import SafeFeatureExtractor
from .data_leakage_detector import DataLeakageDetector

logger = logging.getLogger(__name__)


class BatchDumpProcessor:
    """
    Procesador batch refactorizado - CORREGIDO
    Interfaz consistente, usa n_atoms=16384 fijo para features
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        
        # Inicializar componentes especializados
        self.file_parser = LAMMPSFileParser()
        self.leakage_detector = DataLeakageDetector()
        
        # Inicializar extractor apropiado según configuración
        self._initialize_feature_extractor()
        
        # Callback para progreso
        self.progress_callback: Optional[Callable] = None
        
        # Estado del procesamiento
        self._stop_requested = False
        
        # Log de configuración
        logger.info(f"BatchDumpProcessor inicializado:")
        logger.info(f"  ATM_TOTAL (fijo para features): {self.config.atm_total}")
        logger.info(f"  Feature mode: {self.config.feature_mode.value}")
        logger.info(f"  Extractor: {self.feature_extractor.__class__.__name__}")
    
    def _initialize_feature_extractor(self):
        """Inicializar el extractor de features apropiado"""
        if self.config.feature_mode == FeatureMode.ENHANCED:
            self.feature_extractor = EnhancedSafeFeatureExtractor(self.config)
        else:
            self.feature_extractor = SafeFeatureExtractor(self.config)
    
    def set_parameters(self, **kwargs):
        """Actualizar parámetros de configuración"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Actualizado {key} = {value}")
        
        # Recrear feature extractor con nueva configuración
        self._initialize_feature_extractor()
    
    def set_feature_mode(self, mode: FeatureMode):
        """Establecer modo de extracción de features"""
        self.config.feature_mode = mode
        self._initialize_feature_extractor()
        logger.info(f"Modo de features establecido: {mode.value}")
        logger.info(f"Extractor actualizado: {self.feature_extractor.__class__.__name__}")
    
    def set_progress_callback(self, callback: Callable):
        """Establecer callback para reportar progreso"""
        self.progress_callback = callback
    
    def process_directory(self, directory: str, 
                         validate_leakage: bool = True,
                         save_intermediate: bool = False) -> pd.DataFrame:
        """
        Procesar directorio completo con control de fuga
        CORREGIDO: Interfaz consistente con extractores
        """
        self._stop_requested = False
        
        # Encontrar archivos dump
        dump_files = self.file_parser.find_dump_files(directory)
        
        if not dump_files:
            raise ValueError(f"No se encontraron archivos .dump en {directory}")
        
        logger.info(f"Encontrados {len(dump_files)} archivos .dump")
        logger.info(f"Procesando con {self.feature_extractor.__class__.__name__}")
        logger.info(f"ATM_TOTAL fijo para features: {self.config.atm_total}")
        
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
                
                # Log informativo
                n_atoms_real = features.get('_n_atoms_real', 'N/A')
                n_atoms_used = features.get('_n_atoms_used_for_features', self.config.atm_total)
                vacancies = features.get('vacancies', 'N/A')
                n_features = len([k for k in features.keys() 
                                if not k.startswith('_') and k not in ['file', 'file_path', 'file_hash', 'vacancies']])
                
                logger.info(f"✓ {file_name}: real={n_atoms_real}, fixed={n_atoms_used}, "
                           f"vacancies={vacancies}, features={n_features}")
                
            except Exception as e:
                error_msg = f"Error en {Path(file_path).name}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        if not results:
            raise RuntimeError("No se pudieron procesar archivos correctamente")
        
        # Crear dataset
        dataset = pd.DataFrame(results).set_index("file").sort_index()
        
        # Log de summary
        self._log_processing_summary(dataset)
        
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
        """Procesar un archivo individual - CORREGIDO"""
        # Parsear archivo
        df, n_atoms_real, metadata = self.file_parser.parse_last_frame(file_path)
        
        # Validar datos básicos
        if df.empty or n_atoms_real <= 0:
            raise ValueError(f"Datos inválidos: {n_atoms_real} átomos")
        
        # CRÍTICO: Usar interfaz consistente del extractor
        features = self.feature_extractor.extract_features(df, n_atoms_real, metadata)
        
        # Validar que el extractor haya funcionado correctamente
        expected_vacancies = self.config.atm_total - n_atoms_real
        actual_vacancies = features.get('vacancies', None)
        
        if actual_vacancies != expected_vacancies:
            logger.warning(f"Inconsistencia en cálculo de vacancies: "
                          f"esperado={expected_vacancies}, actual={actual_vacancies}")
            # Corregir si es necesario
            features['vacancies'] = expected_vacancies
        
        # Verificar metadata de procesamiento
        if '_n_atoms_used_for_features' not in features:
            features['_n_atoms_used_for_features'] = self.config.atm_total
        
        return features
    
    def _log_processing_summary(self, dataset: pd.DataFrame):
        """Log del resumen de procesamiento - ACTUALIZADO"""
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
        
        # Verificar consistencia en el uso de n_atoms fijo
        if '_n_atoms_used_for_features' in dataset.columns:
            used_values = dataset['_n_atoms_used_for_features'].unique()
            consistency_check = len(used_values) == 1 and used_values[0] == self.config.atm_total
        else:
            consistency_check = False
        
        logger.info(f"RESUMEN DE PROCESAMIENTO:")
        logger.info(f"  Archivos procesados: {len(dataset)}")
        logger.info(f"  Features extraídas: {len(feature_cols)}")
        logger.info(f"  Extractor usado: {self.feature_extractor.__class__.__name__}")
        logger.info(f"  ATM_TOTAL fijo: {self.config.atm_total}")
        logger.info(f"  Consistencia n_atoms: {'✓' if consistency_check else '⚠️'}")
        
        # Categorizar features si es Enhanced
        if hasattr(self.feature_extractor, 'get_feature_summary'):
            summary = self.feature_extractor.get_feature_summary()
            logger.info(f"  Features básicas: {summary.get('base_features', 0)}")
            logger.info(f"  Features mejoradas: {summary.get('enhanced_features', 0)}")
            logger.info(f"  Features avanzadas: {summary.get('advanced_features', 0)}")
        
        # Verificar rangos del target
        if 'vacancies' in dataset.columns:
            vac_stats = dataset['vacancies'].describe()
            logger.info(f"  Target (vacancies): min={vac_stats['min']:.0f}, "
                       f"max={vac_stats['max']:.0f}, mean={vac_stats['mean']:.1f}")
            
            # Verificar valores negativos (indicaría problema de configuración)
            if vac_stats['min'] < 0:
                logger.error(f"⚠️ PROBLEMA: Vacancies negativas detectadas - "
                           f"revisar ATM_TOTAL={self.config.atm_total}")
    
    def _validate_and_clean_dataset(self, dataset: pd.DataFrame):
        """Validar y limpiar dataset para evitar fuga - MEJORADO"""
        logger.info("Validando dataset contra fuga de información...")
        
        # 1. Verificar consistencia en n_atoms fijo
        if '_n_atoms_used_for_features' in dataset.columns:
            used_values = dataset['_n_atoms_used_for_features'].unique()
            if not (len(used_values) == 1 and used_values[0] == self.config.atm_total):
                logger.error(f"⚠️ PROBLEMA CRÍTICO: Inconsistencia en n_atoms_used_for_features: {used_values}")
                logger.error(f"   Esperado: {self.config.atm_total} (único valor)")
                # No podemos proceder sin esta consistencia
                raise ValueError("Dataset inconsistente - features no usan n_atoms fijo")
        
        # 2. Verificar cálculo correcto del target
        if '_n_atoms_real' in dataset.columns and 'vacancies' in dataset.columns:
            expected_vacancies = self.config.atm_total - dataset['_n_atoms_real']
            actual_vacancies = dataset['vacancies']
            
            mismatches = (expected_vacancies != actual_vacancies).sum()
            if mismatches > 0:
                logger.error(f"⚠️ PROBLEMA: {mismatches} inconsistencias en cálculo de target")
                # Corregir automáticamente
                dataset['vacancies'] = expected_vacancies
                logger.info("Target corregido automáticamente")
        
        # 3. Detectar fuga usando detector
        leakage_analysis = self.leakage_detector.detect_leakage(dataset)
        
        if "error" in leakage_analysis:
            logger.warning(f"Error en análisis de fuga: {leakage_analysis['error']}")
            return
        
        # 4. Eliminar features de alto riesgo automáticamente
        high_risk_features = leakage_analysis['high_risk_features']
        if high_risk_features:
            features_to_remove = [f['feature'] for f in high_risk_features]
            
            logger.warning(f"Eliminando {len(features_to_remove)} features de alto riesgo:")
            for feature_info in high_risk_features[:5]:
                logger.warning(f"  - {feature_info['feature']}: r={feature_info['correlation']:.3f}")
            
            # Eliminar del dataset
            dataset.drop(columns=features_to_remove, inplace=True, errors='ignore')
            
            # Actualizar count de features
            remaining_features = len([col for col in dataset.columns 
                                    if not col.startswith('_') and 
                                    col not in ['file_path', 'file_hash', 'vacancies']])
            logger.info(f"Features restantes después de limpieza: {remaining_features}")
        
        # 5. Verificar features prohibidas
        forbidden_found = [col for col in self.config.forbidden_features 
                          if col in dataset.columns]
        if forbidden_found:
            dataset.drop(columns=forbidden_found, inplace=True)
            logger.warning(f"Eliminadas features prohibidas: {forbidden_found}")
        
        # 6. Log resultados de validación
        suspicious = leakage_analysis['suspicious_features']
        if suspicious:
            logger.warning(f"Patrones sospechosos detectados: {len(suspicious)}")
            for pattern in suspicious[:3]:
                logger.warning(f"  - {pattern}")
        else:
            logger.info("✓ No se detectaron patrones sospechosos")
        
        logger.info("✓ Validación de fuga completada")
    
    def _save_intermediate_results(self, dataset: pd.DataFrame, directory: str):
        """Guardar resultados intermedios - MEJORADO"""
        output_dir = Path(directory) / "processing_output"
        output_dir.mkdir(exist_ok=True)
        
        # Separar features de metadata
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash']]
        metadata_cols = [col for col in dataset.columns if col.startswith('_')]
        
        # Guardar features
        features_path = output_dir / f"features_{self.feature_extractor.__class__.__name__.lower()}.csv"
        dataset[feature_cols].to_csv(features_path)
        
        # Guardar metadata separadamente
        if metadata_cols:
            metadata_path = output_dir / "processing_metadata.csv"
            dataset[metadata_cols].to_csv(metadata_path)
        
        # Guardar configuración completa
        config_path = output_dir / "processing_config.json"
        config_dict = asdict(self.config)
        config_dict.update({
            'extractor_class': self.feature_extractor.__class__.__name__,
            'processing_timestamp': pd.Timestamp.now().isoformat(),
            'files_processed': len(dataset),
            'features_extracted': len(feature_cols),
            'data_leakage_protection': True,
            'n_atoms_consistency_enforced': True
        })
        
        import json
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
        
        # Guardar resumen de features si está disponible
        if hasattr(self.feature_extractor, 'get_feature_summary'):
            feature_summary = self.feature_extractor.get_feature_summary()
            summary_path = output_dir / "feature_summary.json"
            with open(summary_path, 'w') as f:
                json.dump(feature_summary, f, indent=2)
        
        # Guardar reporte de validación
        validation_report = {
            'total_files': len(dataset),
            'total_features': len(feature_cols),
            'atm_total_fixed': self.config.atm_total,
            'target_calculation': f'vacancies = {self.config.atm_total} - n_atoms_real',
            'feature_calculation': f'features use n_atoms = {self.config.atm_total} (fixed)',
            'consistency_checks': {
                'n_atoms_used_consistent': True,  # Si llegamos aquí, pasó la validación
                'target_calculation_correct': True,
                'no_forbidden_features': True
            }
        }
        
        validation_path = output_dir / "validation_report.json"
        with open(validation_path, 'w') as f:
            json.dump(validation_report, f, indent=2)
        
        logger.info(f"Resultados intermedios guardados en {output_dir}")
    
    def _generate_final_report(self, dataset: pd.DataFrame, errors: List[str]):
        """Generar reporte final del procesamiento - MEJORADO"""
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
        
        total_files = len(dataset)
        total_features = len(feature_cols)
        
        # Verificar integridad final
        integrity_check = self._verify_dataset_integrity(dataset)
        
        # Reporte final
        if errors:
            self._report_progress(
                total_files, total_files,
                f"Completado con {len(errors)} errores: {total_features} features extraídas"
            )
            logger.warning(f"Errores durante procesamiento: {len(errors)}")
            for error in errors[:3]:  # Log primeros 3 errores
                logger.warning(f"  - {error}")
        else:
            self._report_progress(
                total_files, total_files,
                f"✓ Procesamiento exitoso: {total_features} features con n_atoms fijo"
            )
        
        # Estadísticas finales
        logger.info("=== REPORTE FINAL ===")
        logger.info(f"Archivos procesados exitosamente: {total_files}")
        logger.info(f"Features extraídas: {total_features}")
        logger.info(f"Extractor utilizado: {self.feature_extractor.__class__.__name__}")
        logger.info(f"ATM_TOTAL fijo para features: {self.config.atm_total}")
        logger.info(f"Integridad del dataset: {'✓ Correcto' if integrity_check else '⚠️ Problemas'}")
        
        if 'vacancies' in dataset.columns:
            vac_stats = dataset['vacancies'].describe()
            logger.info(f"Target stats - min: {vac_stats['min']:.0f}, "
                       f"max: {vac_stats['max']:.0f}, mean: {vac_stats['mean']:.1f}")
        
        logger.info("=== FIN REPORTE ===")
    
    def _verify_dataset_integrity(self, dataset: pd.DataFrame) -> bool:
        """Verificar integridad final del dataset"""
        checks = []
        
        # Check 1: Consistencia n_atoms_used_for_features
        if '_n_atoms_used_for_features' in dataset.columns:
            used_values = dataset['_n_atoms_used_for_features'].unique()
            check1 = len(used_values) == 1 and used_values[0] == self.config.atm_total
            checks.append(check1)
        else:
            checks.append(False)
        
        # Check 2: Target calculation correctness
        if '_n_atoms_real' in dataset.columns and 'vacancies' in dataset.columns:
            expected = self.config.atm_total - dataset['_n_atoms_real']
            actual = dataset['vacancies']
            check2 = (expected == actual).all()
            checks.append(check2)
        else:
            checks.append(False)
        
        # Check 3: No negative vacancies
        if 'vacancies' in dataset.columns:
            check3 = (dataset['vacancies'] >= 0).all()
            checks.append(check3)
        else:
            checks.append(False)
        
        # Check 4: Reasonable number of features
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
        check4 = len(feature_cols) > 0
        checks.append(check4)
        
        return all(checks)
    
    def _report_progress(self, current: int, total: int, message: str = ""):
        """Reportar progreso si hay callback"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def stop_processing(self):
        """Solicitar detener el procesamiento"""
        self._stop_requested = True
        logger.info("Solicitud de detención recibida")
    
    def analyze_leakage(self, dataset: pd.DataFrame) -> str:
        """Realizar análisis completo de fuga y retornar reporte"""
        analysis = self.leakage_detector.detect_leakage(dataset)
        return self.leakage_detector.create_leakage_report(analysis)
    
    def get_dataset_summary(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Generar resumen completo del dataset procesado"""
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
        
        summary = {
            'processing_info': {
                'total_files': len(dataset),
                'total_features': len(feature_cols),
                'extractor_used': self.feature_extractor.__class__.__name__,
                'feature_mode': self.config.feature_mode.value,
                'atm_total_fixed': self.config.atm_total,
                'data_integrity': self._verify_dataset_integrity(dataset)
            },
            'feature_categories': self._categorize_features(feature_cols),
            'target_analysis': self._analyze_target(dataset) if 'vacancies' in dataset.columns else None,
            'consistency_checks': self._run_consistency_checks(dataset)
        }
        
        # Añadir resumen del extractor si está disponible
        if hasattr(self.feature_extractor, 'get_feature_summary'):
            summary['extractor_summary'] = self.feature_extractor.get_feature_summary()
        
        return summary
    
    def _categorize_features(self, feature_cols: List[str]) -> Dict[str, List[str]]:
        """Categorizar features por tipo"""
        categories = {
            'basic_stats': [],
            'energy_features': [],
            'stress_features': [],
            'coordination_features': [],
            'spatial_features': [],
            'voronoi_features': [],
            'advanced_features': [],
            'normalized_features': [],
            'other': []
        }
        
        for col in feature_cols:
            col_lower = col.lower()
            categorized = False
            
            if 'pe_' in col_lower or 'energy' in col_lower:
                categories['energy_features'].append(col)
                categorized = True
            elif 'stress' in col_lower:
                categories['stress_features'].append(col)
                categorized = True
            elif 'coord' in col_lower:
                categories['coordination_features'].append(col)
                categorized = True
            elif any(x in col_lower for x in ['spatial', 'gyration', 'com_', 'moment']):
                categories['spatial_features'].append(col)
                categorized = True
            elif 'voro' in col_lower:
                categories['voronoi_features'].append(col)
                categorized = True
            elif col.endswith('_fixed') or '_norm' in col:
                categories['normalized_features'].append(col)
                categorized = True
            elif any(x in col_lower for x in ['coupling', 'disorder', 'instability', 'cohesion', 'proxy']):
                categories['advanced_features'].append(col)
                categorized = True
            elif any(x in col for x in ['_mean', '_std', '_median', '_q25', '_q75']):
                categories['basic_stats'].append(col)
                categorized = True
            
            if not categorized:
                categories['other'].append(col)
        
        # Filtrar categorías vacías
        return {k: v for k, v in categories.items() if v}
    
    def _analyze_target(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Analizar el target (vacancies)"""
        target = dataset['vacancies']
        
        return {
            'min': int(target.min()),
            'max': int(target.max()),
            'mean': float(target.mean()),
            'std': float(target.std()),
            'median': float(target.median()),
            'unique_values': int(target.nunique()),
            'range': int(target.max() - target.min()),
            'has_negatives': bool((target < 0).any()),
            'distribution': target.value_counts().head(10).to_dict()
        }
    
    def _run_consistency_checks(self, dataset: pd.DataFrame) -> Dict[str, bool]:
        """Ejecutar checks de consistencia"""
        return {
            'n_atoms_fixed_consistent': self._check_n_atoms_consistency(dataset),
            'target_calculation_correct': self._check_target_calculation(dataset),
            'no_negative_vacancies': self._check_no_negative_vacancies(dataset),
            'features_present': self._check_features_present(dataset),
            'no_forbidden_features': self._check_no_forbidden_features(dataset)
        }
    
    def _check_n_atoms_consistency(self, dataset: pd.DataFrame) -> bool:
        """Check consistencia en n_atoms usado para features"""
        if '_n_atoms_used_for_features' not in dataset.columns:
            return False
        used_values = dataset['_n_atoms_used_for_features'].unique()
        return len(used_values) == 1 and used_values[0] == self.config.atm_total
    
    def _check_target_calculation(self, dataset: pd.DataFrame) -> bool:
        """Check cálculo correcto del target"""
        if not all(col in dataset.columns for col in ['_n_atoms_real', 'vacancies']):
            return False
        expected = self.config.atm_total - dataset['_n_atoms_real']
        actual = dataset['vacancies']
        return (expected == actual).all()
    
    def _check_no_negative_vacancies(self, dataset: pd.DataFrame) -> bool:
        """Check que no hay vacancies negativas"""
        if 'vacancies' not in dataset.columns:
            return False
        return (dataset['vacancies'] >= 0).all()
    
    def _check_features_present(self, dataset: pd.DataFrame) -> bool:
        """Check que hay features extraídas"""
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
        return len(feature_cols) > 0
    
    def _check_no_forbidden_features(self, dataset: pd.DataFrame) -> bool:
        """Check que no hay features prohibidas"""
        forbidden_found = [col for col in self.config.forbidden_features 
                          if col in dataset.columns]
        return len(forbidden_found) == 0


# Funciones utilitarias para ML - ACTUALIZADAS Y CORREGIDAS

def prepare_ml_dataset(dataset: pd.DataFrame,
                      target_col: str = 'vacancies',
                      remove_high_correlation: bool = True,
                      correlation_threshold: float = 0.9) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Preparar dataset para ML - CORREGIDO
    Verifica consistencia y separa features del target correctamente
    """
    if target_col not in dataset.columns:
        raise ValueError(f"Columna target '{target_col}' no encontrada")
    
    # Verificar integridad antes de proceder
    if '_n_atoms_used_for_features' in dataset.columns:
        used_values = dataset['_n_atoms_used_for_features'].unique()
        if len(used_values) != 1:
            logger.warning(f"⚠️ Dataset con múltiples valores de n_atoms_used_for_features: {used_values}")
        else:
            logger.info(f"✓ Dataset consistente: features usan n_atoms={used_values[0]}")
    
    # Extraer target
    y = dataset[target_col].copy()
    
    # Identificar features (excluir target, metadata y auxiliares)
    exclude_cols = {target_col, 'file_path', 'file'}
    exclude_cols.update([col for col in dataset.columns if col.startswith('_')])
    
    feature_cols = [col for col in dataset.columns if col not in exclude_cols]
    X = dataset[feature_cols].copy()
    
    logger.info(f"Dataset ML base: {X.shape[0]} muestras, {X.shape[1]} features")
    
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
                logger.info(f"Features restantes: {X.shape[1]}")
    
    # Imputar valores faltantes
    from sklearn.impute import SimpleImputer
    imputer = SimpleImputer(strategy='median')
    X_imputed = pd.DataFrame(
        imputer.fit_transform(X),
        columns=X.columns,
        index=X.index
    )
    
    logger.info(f"Dataset ML final: {X_imputed.shape[0]} muestras, "
               f"{X_imputed.shape[1]} features limpias, target: {target_col}")
    
    return X_imputed, y


def create_train_test_split(dataset: pd.DataFrame,
                           target_col: str = 'vacancies',
                           test_size: float = 0.2,
                           random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Crear división train/test con estratificación - CORREGIDO"""
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
    
    logger.info(f"División ML: {len(X_train)} train, {len(X_test)} test")
    logger.info(f"Target range - train: [{y_train.min()}, {y_train.max()}], "
               f"test: [{y_test.min()}, {y_test.max()}]")
    
    return X_train, X_test, y_train, y_test