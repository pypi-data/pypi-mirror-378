"""
Procesador batch refactorizado - ACTUALIZADO
Sin dependencia de n_atoms en features - Solo para cálculo de vacancies
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
from .feature_extractor import SafeFeatureExtractor
from .data_leakage_detector import DataLeakageDetector

logger = logging.getLogger(__name__)


class BatchDumpProcessor:
    """
    Procesador batch refactorizado con separación de responsabilidades
    y control estricto de fuga de información
    
    ACTUALIZADO: Ya no usa n_atoms para normalización de features
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        
        # Inicializar componentes especializados
        self.file_parser = LAMMPSFileParser()
        self.feature_extractor = SafeFeatureExtractor(self.config)
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
        Procesar directorio completo con control de fuga
        
        Args:
            directory: Directorio con archivos .dump
            validate_leakage: Si validar contra fuga de información
            save_intermediate: Si guardar resultados intermedios
            
        Returns:
            DataFrame con features extraídas
        """
        logger.info(f"Iniciando procesamiento de directorio: {directory}")
        
        # Encontrar archivos
        dump_files = self.find_dump_files(directory)
        if not dump_files:
            raise ValueError(f"No se encontraron archivos .dump en {directory}")
        
        logger.info(f"Encontrados {len(dump_files)} archivos para procesar")
        
        # Procesar archivos
        results = []
        errors = []
        
        for i, file_path in enumerate(dump_files):
            if self._stop_requested:
                logger.info("Procesamiento detenido por solicitud del usuario")
                break
                
            try:
                # Reportar progreso
                if self.progress_callback:
                    self.progress_callback(i, len(dump_files), f"Procesando {Path(file_path).name}")
                
                # Procesar archivo individual
                features = self._process_single_file(file_path)
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
        
        # Validar contra fuga de información
        if validate_leakage:
            self._validate_and_clean_dataset(dataset)
        
        # Reportar resultados finales
        if self.progress_callback:
            self.progress_callback(len(dump_files), len(dump_files), "Completado")
        
        # Generar reporte
        self._generate_final_report(dataset, errors)
        
        return dataset
    
    def _process_single_file(self, file_path: str) -> Dict[str, Any]:
        """
        Procesar un archivo individual
        
        ACTUALIZADO: Ya no pasa n_atoms como parámetro a extract_features
        """
        # Parsear archivo
        df, n_atoms, metadata = self.file_parser.parse_last_frame(file_path)
        
        # Validar datos básicos
        if df.empty or n_atoms <= 0:
            raise ValueError(f"Datos inválidos: {n_atoms} átomos")
        
        # ACTUALIZADO: extract_features ya no necesita n_atoms como parámetro
        # El número de átomos se calcula internamente como len(df)
        features = self.feature_extractor.extract_features(df, metadata)
        
        # Agregar metadata de procesamiento (solo para información)
        features["_n_atoms_in_file"] = n_atoms  # Solo para referencia/debugging
        features["_processing_mode"] = self.config.feature_mode.value
        features["_file_path"] = file_path
        
        # Verificar que el cálculo de vacancies sea consistente
        calculated_vacancies = self.config.atm_total - n_atoms
        if features.get("vacancies") != calculated_vacancies:
            logger.warning(f"Inconsistencia en cálculo de vacancies: "
                         f"esperado {calculated_vacancies}, obtenido {features.get('vacancies')}")
        
        return features
    
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
    
    def _generate_final_report(self, dataset: pd.DataFrame, errors: List[Dict]):
        """Generar reporte final del procesamiento"""
        logger.info("=" * 50)
        logger.info("REPORTE FINAL DE PROCESAMIENTO")
        logger.info("=" * 50)
        
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
        return {
            "atm_total": self.config.atm_total,
            "energy_range": (self.config.energy_min, self.config.energy_max),
            "energy_bins": self.config.energy_bins,
            "feature_mode": self.config.feature_mode.value,
            "add_noise": self.config.add_noise,
            "noise_level": self.config.noise_level if self.config.add_noise else None,
            "forbidden_features": list(self.config.forbidden_features),
            "validate_features": self.config.validate_features
        }
    
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
        
        # Validar configuración de ruido
        if self.config.add_noise and self.config.noise_level <= 0:
            warnings.append("add_noise está activado pero noise_level no es positivo")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }


# Función auxiliar para crear procesador con configuración típica
def create_standard_processor(atm_total: int = 16384,
                            energy_min: float = -4.0,
                            energy_max: float = -3.0,
                            energy_bins: int = 10,
                            feature_mode: FeatureMode = FeatureMode.STANDARD) -> BatchDumpProcessor:
    """
    Crear procesador con configuración estándar
    
    Args:
        atm_total: Número total de átomos en cristal perfecto
        energy_min: Energía mínima para histogramas
        energy_max: Energía máxima para histogramas
        energy_bins: Número de bins para histogramas de energía
        feature_mode: Modo de extracción de features
        
    Returns:
        Procesador configurado y listo para usar
    """
    config = ProcessingConfig(
        atm_total=atm_total,
        energy_min=energy_min,
        energy_max=energy_max,
        energy_bins=energy_bins,
        feature_mode=feature_mode,
        add_noise=False,
        validate_features=True
    )
    
    return BatchDumpProcessor(config)