"""
Detector de fuga de información - Análisis de correlaciones sospechosas
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Tuple, Optional
import logging
from .config import CORRELATION_THRESHOLD

logger = logging.getLogger(__name__)


class DataLeakageDetector:
    """Detector especializado en identificar fuga de información en datasets"""
    
    def __init__(self, correlation_threshold: float = CORRELATION_THRESHOLD):
        self.correlation_threshold = correlation_threshold
        self._feature_correlations = {}
    
    def detect_leakage(self, dataset: pd.DataFrame, 
                      target_col: str = 'vacancies') -> Dict[str, Any]:
        """
        Detectar posibles fugas de información
        
        Returns:
            Diccionario con análisis completo de fuga
        """
        if target_col not in dataset.columns:
            return {"error": f"Columna target '{target_col}' no encontrada"}
        
        # Separar features del target y metadata
        feature_cols = self._identify_feature_columns(dataset, target_col)
        
        if not feature_cols:
            return {"error": "No se encontraron features para analizar"}
        
        # Calcular correlaciones
        correlations = self._calculate_correlations(dataset, feature_cols, target_col)
        
        # Análisis de fuga
        leakage_analysis = {
            "total_features": len(feature_cols),
            "correlations": correlations,
            "high_risk_features": self._identify_high_risk_features(correlations),
            "suspicious_features": self._identify_suspicious_patterns(correlations),
            "recommendations": self._generate_recommendations(correlations),
            "data_quality": self._assess_data_quality(dataset, feature_cols),
            "target_distribution": self._analyze_target_distribution(dataset, target_col)
        }
        
        # Almacenar correlaciones para validación futura
        self._feature_correlations = {corr['feature']: corr['correlation'] 
                                    for corr in correlations}
        
        return leakage_analysis
    
    def _identify_feature_columns(self, dataset: pd.DataFrame, target_col: str) -> List[str]:
        """Identificar columnas que son features (no metadata ni target)"""
        exclude_cols = {
            target_col, 'file_path', 'file_hash', 'file'
        }
        
        # Excluir columnas que empiecen con _
        exclude_cols.update([col for col in dataset.columns if col.startswith('_')])
        
        feature_cols = [col for col in dataset.columns if col not in exclude_cols]
        
        return feature_cols
    
    def _calculate_correlations(self, dataset: pd.DataFrame, 
                              feature_cols: List[str], target_col: str) -> List[Dict]:
        """Calcular correlaciones entre features y target"""
        correlations = []
        
        for col in feature_cols:
            if dataset[col].dtype in [np.float64, np.int64, np.float32, np.int32]:
                try:
                    corr = dataset[col].corr(dataset[target_col])
                    if not np.isnan(corr):
                        correlations.append({
                            'feature': col,
                            'correlation': float(corr),
                            'abs_correlation': float(abs(corr)),
                            'risk_level': self._classify_risk_level(abs(corr))
                        })
                except Exception as e:
                    logger.warning(f"Error calculando correlación para {col}: {str(e)}")
        
        # Ordenar por correlación absoluta
        correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
        
        return correlations
    
    def _classify_risk_level(self, abs_corr: float) -> str:
        """Clasificar nivel de riesgo basado en correlación absoluta"""
        if abs_corr > 0.9:
            return 'critical'  # Muy probable fuga
        elif abs_corr > 0.7:
            return 'high'      # Alta probabilidad de fuga
        elif abs_corr > 0.4:
            return 'medium'    # Moderada preocupación
        else:
            return 'low'       # Bajo riesgo
    
    def _identify_high_risk_features(self, correlations: List[Dict]) -> List[Dict]:
        """Identificar features de alto riesgo"""
        return [corr for corr in correlations 
                if corr['abs_correlation'] > self.correlation_threshold]
    
    def _identify_suspicious_patterns(self, correlations: List[Dict]) -> List[str]:
        """Identificar patrones sospechosos en nombres de features"""
        suspicious_patterns = []
        
        for corr in correlations:
            feature_name = corr['feature'].lower()
            
            # Patrones que sugieren fuga directa
            if any(pattern in feature_name for pattern in [
                'vacancy', 'n_atom', 'atom_count', 'missing', 'defect_count'
            ]):
                suspicious_patterns.append(f"{corr['feature']} - nombre sospechoso")
            
            # Features con correlación perfecta o casi perfecta
            if corr['abs_correlation'] > 0.99:
                suspicious_patterns.append(f"{corr['feature']} - correlación casi perfecta")
        
        return suspicious_patterns
    
    def _generate_recommendations(self, correlations: List[Dict]) -> List[str]:
        """Generar recomendaciones basadas en el análisis"""
        recommendations = []
        
        critical_features = [c for c in correlations if c['risk_level'] == 'critical']
        high_risk_features = [c for c in correlations if c['risk_level'] == 'high']
        
        if critical_features:
            recommendations.append(
                f"CRÍTICO: Eliminar inmediatamente {len(critical_features)} features "
                f"con correlación >0.9: {[f['feature'] for f in critical_features[:3]]}"
            )
        
        if high_risk_features:
            recommendations.append(
                f"ALTO RIESGO: Revisar {len(high_risk_features)} features "
                f"con correlación >0.7"
            )
        
        if len(correlations) > 50:
            recommendations.append(
                "Considerar reducción de dimensionalidad - muchas features pueden "
                "introducir ruido o correlaciones espurias"
            )
        
        # Recomendaciones específicas de validación
        recommendations.extend([
            "Validar con validación cruzada estratificada",
            "Usar conjunto de validación completamente independiente",
            "Monitorear métricas en datos no vistos"
        ])
        
        return recommendations
    
    def _assess_data_quality(self, dataset: pd.DataFrame, 
                           feature_cols: List[str]) -> Dict[str, Any]:
        """Evaluar calidad general de los datos"""
        quality_metrics = {}
        
        # Valores faltantes
        null_counts = dataset[feature_cols].isnull().sum()
        quality_metrics['features_with_nulls'] = int((null_counts > 0).sum())
        quality_metrics['total_null_ratio'] = float(null_counts.sum() / 
                                                   (len(dataset) * len(feature_cols)))
        
        # Valores infinitos
        inf_counts = dataset[feature_cols].apply(lambda x: np.isinf(x).sum() if x.dtype in [np.float64, np.int64] else 0)
        quality_metrics['features_with_inf'] = int((inf_counts > 0).sum())
        
        # Varianza cero (features constantes)
        zero_var_features = []
        for col in feature_cols:
            if dataset[col].dtype in [np.float64, np.int64]:
                if dataset[col].std() == 0:
                    zero_var_features.append(col)
        
        quality_metrics['zero_variance_features'] = zero_var_features
        quality_metrics['zero_variance_count'] = len(zero_var_features)
        
        return quality_metrics
    
    def _analyze_target_distribution(self, dataset: pd.DataFrame, 
                                   target_col: str) -> Dict[str, Any]:
        """Analizar distribución del target"""
        target_series = dataset[target_col]
        
        distribution = {
            'min': float(target_series.min()),
            'max': float(target_series.max()),
            'mean': float(target_series.mean()),
            'std': float(target_series.std()),
            'median': float(target_series.median()),
            'unique_values': int(target_series.nunique()),
            'is_balanced': self._assess_balance(target_series)
        }
        
        return distribution
    
    def _assess_balance(self, target_series: pd.Series) -> bool:
        """Evaluar si el target está balanceado"""
        if target_series.nunique() < 10:  # Categórico
            value_counts = target_series.value_counts()
            min_ratio = value_counts.min() / value_counts.max()
            return min_ratio > 0.1  # Al menos 10% en cada clase
        else:  # Continuo
            # Usar cuartiles para evaluar balance
            q1, q3 = target_series.quantile([0.25, 0.75])
            iqr = q3 - q1
            return iqr > 0  # Hay variabilidad
    
    def validate_features_against_history(self, features: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validar features contra historial de correlaciones conocidas"""
        warnings = []
        is_valid = True
        
        for feature_name, value in features.items():
            if feature_name in self._feature_correlations:
                stored_corr = abs(self._feature_correlations[feature_name])
                if stored_corr > self.correlation_threshold:
                    warnings.append(
                        f"Feature '{feature_name}' tiene historial de alta correlación "
                        f"con target ({stored_corr:.3f})"
                    )
                    is_valid = False
        
        return is_valid, warnings
    
    def create_leakage_report(self, analysis: Dict[str, Any]) -> str:
        """Crear reporte legible del análisis de fuga"""
        if "error" in analysis:
            return f"Error en análisis: {analysis['error']}"
        
        report_lines = [
            "=== REPORTE DE ANÁLISIS DE FUGA DE INFORMACIÓN ===\n",
            f"Total de features analizadas: {analysis['total_features']}",
            f"Umbral de correlación crítico: {self.correlation_threshold}\n"
        ]
        
        # Features de alto riesgo
        high_risk = analysis['high_risk_features']
        if high_risk:
            report_lines.extend([
                f"⚠️  FEATURES DE ALTO RIESGO: {len(high_risk)}",
                "-" * 50
            ])
            
            for feature in high_risk[:10]:  # Top 10
                report_lines.append(
                    f"  {feature['feature']}: {feature['correlation']:.4f} "
                    f"({feature['risk_level']})"
                )
            
            if len(high_risk) > 10:
                report_lines.append(f"  ... y {len(high_risk) - 10} más\n")
        else:
            report_lines.append("✅ No se detectaron features de alto riesgo\n")
        
        # Patrones sospechosos
        suspicious = analysis['suspicious_features']
        if suspicious:
            report_lines.extend([
                f"🔍 PATRONES SOSPECHOSOS: {len(suspicious)}",
                "-" * 50
            ])
            for pattern in suspicious[:5]:
                report_lines.append(f"  - {pattern}")
            report_lines.append("")
        
        # Recomendaciones
        recommendations = analysis['recommendations']
        if recommendations:
            report_lines.extend([
                "📋 RECOMENDACIONES:",
                "-" * 50
            ])
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"  {i}. {rec}")
            report_lines.append("")
        
        # Calidad de datos
        quality = analysis['data_quality']
        report_lines.extend([
            "📊 CALIDAD DE DATOS:",
            "-" * 50,
            f"  - Features con valores nulos: {quality['features_with_nulls']}",
            f"  - Ratio de valores nulos: {quality['total_null_ratio']:.2%}",
            f"  - Features con varianza cero: {quality['zero_variance_count']}"
        ])
        
        if quality['zero_variance_features']:
            report_lines.append(f"    {quality['zero_variance_features'][:3]}")
        
        return "\n".join(report_lines)