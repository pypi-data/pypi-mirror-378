"""
Procesador batch actualizado con integración opcional de Ovito - VERSIÓN CORREGIDA
Permite elegir entre procesamiento tradicional y procesamiento con pipeline Ovito
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Callable
import logging
import threading
from dataclasses import asdict
from enum import Enum

# CORREGIDO: Importar el BatchDumpProcessor original del proyecto
from .batch_processor import BatchDumpProcessor  # Procesador original
from .config import ProcessingConfig, FeatureMode
from .data_leakage_detector import DataLeakageDetector

# Importar el nuevo procesador Ovito corregido
try:
    from .ovito_integrated_batch_processor import OvitoIntegratedBatchProcessor
    OVITO_PROCESSOR_AVAILABLE = True
except ImportError as e:
    OVITO_PROCESSOR_AVAILABLE = False
    OVITO_PROCESSOR_ERROR = str(e)

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Modos de procesamiento disponibles"""
    TRADITIONAL = "traditional"     # Procesamiento tradicional sin Ovito
    OVITO_SURFACE_REMOVAL = "ovito_surface_removal"  # Con eliminación de superficie Ovito


class UnifiedBatchDumpProcessor:
    """
    Procesador batch unificado que soporta múltiples modos de procesamiento:
    - Tradicional: Usando el BatchDumpProcessor original del proyecto
    - Ovito: Con pipeline de eliminación de superficie (si está disponible)
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None, 
                 processing_mode: ProcessingMode = ProcessingMode.TRADITIONAL):
        self.config = config or ProcessingConfig()
        self.processing_mode = processing_mode
        
        # CORREGIDO: Validar disponibilidad de Ovito si se solicita
        if processing_mode == ProcessingMode.OVITO_SURFACE_REMOVAL and not OVITO_PROCESSOR_AVAILABLE:
            logger.warning(f"Ovito no disponible: {OVITO_PROCESSOR_ERROR}")
            logger.info("Cambiando a modo tradicional")
            processing_mode = ProcessingMode.TRADITIONAL
            self.processing_mode = processing_mode
        
        # Inicializar procesador según el modo
        self.processor = self._create_processor(processing_mode)
        
        # Callback para progreso
        self.progress_callback: Optional[Callable] = None
        
        logger.info(f"Procesador inicializado en modo: {self.processing_mode.value}")
    
    def _create_processor(self, mode: ProcessingMode):
        """CORREGIDO: Factory method para crear procesador según modo"""
        if mode == ProcessingMode.OVITO_SURFACE_REMOVAL:
            if OVITO_PROCESSOR_AVAILABLE:
                processor = OvitoIntegratedBatchProcessor(self.config)
                logger.debug("Creado procesador con pipeline Ovito")
                return processor
            else:
                logger.warning("Ovito no disponible, usando procesador tradicional")
                mode = ProcessingMode.TRADITIONAL
                self.processing_mode = mode
        
        # Usar el BatchDumpProcessor original del proyecto
        processor = BatchDumpProcessor(self.config)
        logger.debug("Creado procesador tradicional")
        return processor
    
    def set_processing_mode(self, mode: ProcessingMode):
        """Cambiar modo de procesamiento"""
        if mode == self.processing_mode:
            logger.debug(f"Ya está en modo {mode.value}")
            return
        
        # Validar disponibilidad de Ovito
        if mode == ProcessingMode.OVITO_SURFACE_REMOVAL and not OVITO_PROCESSOR_AVAILABLE:
            logger.error(f"No se puede cambiar a modo Ovito: {OVITO_PROCESSOR_ERROR}")
            raise RuntimeError("Procesador Ovito no disponible")
        
        old_mode = self.processing_mode
        self.processing_mode = mode
        
        # Recrear procesador con nueva configuración
        try:
            self.processor = self._create_processor(mode)
            
            # Transferir callback si existe
            if self.progress_callback:
                self.processor.set_progress_callback(self.progress_callback)
            
            logger.info(f"Cambiado de modo {old_mode.value} a {mode.value}")
            
        except Exception as e:
            # Rollback en caso de error
            self.processing_mode = old_mode
            logger.error(f"Error cambiando modo: {str(e)}")
            raise
    
    def set_ovito_parameters(self, surface_radius: float = 2.5, smoothing_level: int = 8):
        """Configurar parámetros específicos de Ovito (solo si está en modo Ovito)"""
        if self.processing_mode == ProcessingMode.OVITO_SURFACE_REMOVAL:
            if hasattr(self.processor, 'set_ovito_parameters'):
                self.processor.set_ovito_parameters(surface_radius, smoothing_level)
                logger.info(f"Parámetros Ovito actualizados: radius={surface_radius}, smoothing={smoothing_level}")
            else:
                logger.warning("El procesador actual no soporta parámetros Ovito")
        else:
            logger.warning("Los parámetros de Ovito solo aplican en modo OVITO_SURFACE_REMOVAL")
    
    def set_parameters(self, **kwargs):
        """Actualizar parámetros de configuración"""
        # Validar parámetros
        valid_params = {}
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                valid_params[key] = value
                logger.debug(f"Actualizado {key} = {value}")
            else:
                logger.warning(f"Parámetro desconocido ignorado: {key}")
        
        if valid_params:
            # Actualizar en el procesador activo
            if hasattr(self.processor, 'set_parameters'):
                self.processor.set_parameters(**valid_params)
            logger.info(f"Actualizados {len(valid_params)} parámetros")
    
    def set_feature_mode(self, mode: FeatureMode):
        """Establecer modo de extracción de features"""
        if not isinstance(mode, FeatureMode):
            raise ValueError(f"mode debe ser una instancia de FeatureMode")
        
        self.config.feature_mode = mode
        
        if hasattr(self.processor, 'set_feature_mode'):
            self.processor.set_feature_mode(mode)
        
        logger.info(f"Modo de features establecido: {mode.value}")
    
    def set_progress_callback(self, callback: Callable):
        """Establecer callback para reportar progreso"""
        if callback and not callable(callback):
            raise ValueError("callback debe ser callable")
        
        self.progress_callback = callback
        
        if hasattr(self.processor, 'set_progress_callback'):
            self.processor.set_progress_callback(callback)
    
    def process_directory(self, directory: str, 
                         validate_leakage: bool = True,
                         save_intermediate: bool = False) -> pd.DataFrame:
        """
        Procesar directorio completo usando el modo seleccionado
        
        Args:
            directory: Directorio con archivos .dump
            validate_leakage: Si validar fuga de información
            save_intermediate: Si guardar resultados intermedios
            
        Returns:
            DataFrame con features extraídas según el modo de procesamiento
        """
        # Validar entrada
        if not directory or not Path(directory).exists():
            raise ValueError(f"Directorio no válido: {directory}")
        
        logger.info(f"Procesando directorio con modo: {self.processing_mode.value}")
        logger.info(f"Directorio: {directory}")
        logger.info(f"Validar fuga: {validate_leakage}, Guardar intermedios: {save_intermediate}")
        
        try:
            # Delegar al procesador correspondiente
            dataset = self.processor.process_directory(
                directory=directory,
                validate_leakage=validate_leakage,
                save_intermediate=save_intermediate
            )
            
            # Agregar metadata del procesador unificado
            if not dataset.empty:
                # Agregar información del modo usado (sin modificar el dataset original)
                logger.info(f"Procesamiento completado: {len(dataset)} archivos, modo {self.processing_mode.value}")
            
            return dataset
            
        except Exception as e:
            logger.error(f"Error en procesamiento: {str(e)}")
            raise
    
    def stop_processing(self):
        """Solicitar detener el procesamiento"""
        if hasattr(self.processor, 'stop_processing'):
            self.processor.stop_processing()
            logger.info("Solicitud de detención enviada al procesador")
        else:
            logger.warning("El procesador actual no soporta detención")
    
    def get_feature_summary(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Generar resumen detallado del dataset procesado"""
        if dataset.empty:
            return {"error": "Dataset vacío"}
        
        try:
            # Obtener resumen del procesador específico
            if hasattr(self.processor, 'get_feature_summary'):
                summary = self.processor.get_feature_summary(dataset)
            else:
                # Fallback: crear resumen básico
                feature_cols = [col for col in dataset.columns 
                               if not col.startswith('_') and col not in ['file_path', 'file_hash', 'vacancies']]
                summary = {
                    "processing_info": {
                        "total_files": len(dataset),
                        "total_features": len(feature_cols),
                        "processor_type": type(self.processor).__name__
                    }
                }
            
            # Agregar información del procesador unificado
            summary["unified_processor_info"] = {
                "processing_mode": self.processing_mode.value,
                "processor_class": type(self.processor).__name__,
                "ovito_available": OVITO_PROCESSOR_AVAILABLE,
                "feature_mode": self.config.feature_mode.value
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generando resumen: {str(e)}")
            return {"error": str(e)}
    
    def get_processing_info(self) -> Dict[str, Any]:
        """Obtener información sobre el procesamiento activo"""
        info = {
            "processing_mode": self.processing_mode.value,
            "processor_class": type(self.processor).__name__,
            "feature_mode": self.config.feature_mode.value,
            "ovito_available": OVITO_PROCESSOR_AVAILABLE,
            "configuration": asdict(self.config)
        }
        
        # Agregar información específica de Ovito si aplica y está disponible
        if (self.processing_mode == ProcessingMode.OVITO_SURFACE_REMOVAL and 
            hasattr(self.processor, 'surface_radius')):
            info["ovito_parameters"] = {
                "surface_radius": self.processor.surface_radius,
                "smoothing_level": self.processor.smoothing_level
            }
        
        return info
    
    def analyze_leakage(self, dataset: pd.DataFrame) -> str:
        """Realizar análisis completo de fuga y retornar reporte"""
        if dataset.empty:
            return "Dataset vacío - no se puede analizar fuga"
        
        try:
            # Intentar usar método del procesador específico
            if hasattr(self.processor, 'analyze_leakage'):
                return self.processor.analyze_leakage(dataset)
            else:
                # Fallback usando detector directo
                detector = DataLeakageDetector()
                analysis = detector.detect_leakage(dataset)
                return detector.create_leakage_report(analysis)
                
        except Exception as e:
            error_msg = f"Error en análisis de fuga: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def get_available_modes(self) -> List[str]:
        """Obtener lista de modos de procesamiento disponibles"""
        modes = [ProcessingMode.TRADITIONAL.value]
        
        if OVITO_PROCESSOR_AVAILABLE:
            modes.append(ProcessingMode.OVITO_SURFACE_REMOVAL.value)
        
        return modes
    
    def is_ovito_available(self) -> bool:
        """Verificar si Ovito está disponible"""
        return OVITO_PROCESSOR_AVAILABLE
    
    def get_ovito_error(self) -> Optional[str]:
        """Obtener error de Ovito si no está disponible"""
        return OVITO_PROCESSOR_ERROR if not OVITO_PROCESSOR_AVAILABLE else None


# CORREGIDO: Funciones utilitarias que funcionan con ambos modos

def prepare_ml_dataset_unified(dataset: pd.DataFrame,
                              target_col: str = 'vacancies',
                              remove_high_correlation: bool = True,
                              correlation_threshold: float = 0.9) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Preparar dataset para machine learning (funciona con ambos modos de procesamiento)
    
    Args:
        dataset: DataFrame con features y target
        target_col: Nombre de la columna target
        remove_high_correlation: Si eliminar features con alta correlación
        correlation_threshold: Umbral de correlación para eliminación
        
    Returns:
        Tupla (X, y) con features preparadas y target
    """
    if dataset.empty:
        raise ValueError("Dataset vacío")
    
    if target_col not in dataset.columns:
        raise ValueError(f"Columna target '{target_col}' no encontrada")
    
    # Extraer target
    y = dataset[target_col].copy()
    
    # Identificar features (excluir target, metadata y auxiliares)
    exclude_cols = {target_col, 'file_path', 'file_hash'}
    exclude_cols.update([col for col in dataset.columns if col.startswith('_')])
    
    feature_cols = [col for col in dataset.columns if col not in exclude_cols]
    
    if not feature_cols:
        raise ValueError("No se encontraron features válidas")
    
    X = dataset[feature_cols].copy()
    
    # Eliminar features de alta correlación si está habilitado
    if remove_high_correlation and len(feature_cols) > 1:
        try:
            detector = DataLeakageDetector(correlation_threshold)
            
            # Crear dataset temporal para análisis
            temp_dataset = X.copy()
            temp_dataset[target_col] = y
            
            analysis = detector.detect_leakage(temp_dataset, target_col)
            
            if 'high_risk_features' in analysis and analysis['high_risk_features']:
                features_to_remove = [f['feature'] for f in analysis['high_risk_features']]
                if features_to_remove:
                    # Verificar que no eliminemos todas las features
                    remaining_features = [col for col in X.columns if col not in features_to_remove]
                    if remaining_features:
                        X = X.drop(columns=features_to_remove, errors='ignore')
                        logger.info(f"Eliminadas {len(features_to_remove)} features de alta correlación")
                    else:
                        logger.warning("No se eliminaron features - resultaría en dataset vacío")
        except Exception as e:
            logger.warning(f"Error en eliminación de alta correlación: {str(e)}")
    
    # Imputar valores faltantes si es necesario
    if X.isnull().any().any():
        try:
            from sklearn.impute import SimpleImputer
            imputer = SimpleImputer(strategy='median')
            X_imputed = pd.DataFrame(
                imputer.fit_transform(X),
                columns=X.columns,
                index=X.index
            )
            logger.info("Valores faltantes imputados")
        except Exception as e:
            logger.warning(f"Error en imputación: {str(e)}")
            X_imputed = X.copy()
    else:
        X_imputed = X.copy()
    
    # Detectar modo de procesamiento desde metadata
    processing_mode = "unknown"
    if '_processing_mode' in dataset.columns and len(dataset) > 0:
        try:
            sample_mode = dataset['_processing_mode'].iloc[0]
            if 'ovito' in str(sample_mode).lower():
                processing_mode = "Ovito (superficie removida)"
            elif 'traditional' in str(sample_mode).lower():
                processing_mode = "tradicional"
        except Exception:
            processing_mode = "unknown"
    
    logger.info(f"Dataset ML preparado ({processing_mode}): {X_imputed.shape[0]} muestras, "
               f"{X_imputed.shape[1]} features, target: {target_col}")
    
    return X_imputed, y


def create_train_test_split_unified(dataset: pd.DataFrame,
                                   target_col: str = 'vacancies',
                                   test_size: float = 0.2,
                                   random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Crear división train/test con estratificación (funciona con ambos modos)
    
    Args:
        dataset: DataFrame con features y target
        target_col: Nombre de la columna target
        test_size: Proporción para test
        random_state: Semilla aleatoria
        
    Returns:
        Tupla (X_train, X_test, y_train, y_test)
    """
    try:
        from sklearn.model_selection import train_test_split
        
        X, y = prepare_ml_dataset_unified(dataset, target_col)
        
        # Estratificar por cuartiles del target si es continuo
        if y.nunique() > 10:
            try:
                stratify_bins = pd.qcut(y, q=4, labels=False, duplicates='drop')
            except Exception as e:
                logger.warning(f"Error en estratificación por cuartiles: {str(e)}")
                stratify_bins = None
        else:
            stratify_bins = y
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state,
            stratify=stratify_bins
        )
        
        logger.info(f"División creada: {len(X_train)} train, {len(X_test)} test")
        
        return X_train, X_test, y_train, y_test
        
    except Exception as e:
        logger.error(f"Error en train_test_split: {str(e)}")
        raise


# CORREGIDO: Aliases para mantener compatibilidad hacia atrás
BatchDumpProcessor = UnifiedBatchDumpProcessor
prepare_ml_dataset = prepare_ml_dataset_unified
create_train_test_split = create_train_test_split_unified