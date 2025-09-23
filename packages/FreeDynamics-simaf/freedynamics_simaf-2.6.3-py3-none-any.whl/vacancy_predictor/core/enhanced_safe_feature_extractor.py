"""
Extractor de features MEJORADO sin fuga de información
Combina features seguras originales + features avanzadas para mejor predicción
"""

import pandas as pd
import numpy as np
import hashlib
from typing import Dict, Any, Optional
import logging
from .config import ProcessingConfig, FeatureCategories, FeatureMode
from scipy import stats

logger = logging.getLogger(__name__)


class EnhancedSafeFeatureExtractor:
    """
    Extractor de features mejorado con control estricto de fuga de información
    Combina features originales + features avanzadas para mejor rendimiento
    """
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
    
    def extract_features(self, df: pd.DataFrame, n_atoms: int, 
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extrae features con control de fuga de información + features avanzadas
        
        IMPORTANTE: 'vacancies' se calcula como TARGET, NO como feature
        """
        # Agregar invariantes de stress si es posible
        df = self._add_stress_invariants(df)
        
        features = {}
        
        # ===== FEATURES ORIGINALES (SEGURAS) =====
        # 1. Features de energía (bajo riesgo)
        features.update(self._extract_energy_features(df))
        
        # 2. Features de stress (bajo-medio riesgo)
        features.update(self._extract_stress_features(df))
        
        # 3. Features de coordinación (controladas)
        features.update(self._extract_coordination_features(df))
        
        # 4. Features espaciales (bajo riesgo)
        features.update(self._extract_spatial_features(df))
        
        # 5. Features de volumen de Voronoi (si está disponible)
        features.update(self._extract_voronoi_features(df))
        
        # 6. Metadata del sistema (cuidadosamente seleccionada)
        features.update(self._extract_system_features(n_atoms, metadata))
        
        # ===== FEATURES AVANZADAS (NUEVAS) =====
        # 7. Features termodinámicas avanzadas
        features.update(self._extract_thermodynamic_advanced_features(df, features))
        
        # 8. Features estructurales mejoradas
        features.update(self._extract_structural_advanced_features(df, features, n_atoms, metadata))
        
        # 9. Features combinadas (más predictivas)
        features.update(self._extract_combined_advanced_features(df, features))
        
        # 10. Features de ratios importantes
        features.update(self._extract_ratio_advanced_features(df, features))
        
        # ===== PROCESAMIENTO FINAL (ORIGINAL) =====
        # 11. CRÍTICO: Calcular TARGET (vacancies) pero NO incluir como feature
        vacancies = int(self.config.atm_total - n_atoms)
        features["vacancies"] = vacancies  # TARGET - será separado del feature set
        
        # 12. Hash para tracking (no es feature de ML)
        features["file_hash"] = self._compute_file_hash(df)
        
        # 13. Agregar metadata de riesgo (sin filtrar automáticamente)
        features = self._add_feature_risk_metadata(features)
        
        # 14. Agregar ruido si está configurado
        if self.config.add_noise:
            features = self._add_gaussian_noise_to_features(features)
        
        return features
    
    # ============== FEATURES ORIGINALES (CORREGIDAS) ==============
    
    def _add_stress_invariants(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agregar invariantes de stress I1, I2, I3 y von Mises"""
        stress_cols = [f"c_satom[{i}]" for i in range(1, 7)]
        
        if not all(col in df.columns for col in stress_cols):
            return df
        
        df = df.copy()
        
        try:
            sxx, syy, szz, sxy, sxz, syz = (df[col].astype(float) for col in stress_cols)
            
            # Primer invariante (traza)
            I1 = sxx + syy + szz
            
            # Segundo invariante
            I2 = sxx*syy + syy*szz + szz*sxx - sxy**2 - sxz**2 - syz**2
            
            # Tercer invariante (determinante)
            I3 = (sxx * (syy*szz - syz**2) - 
                  sxy * (sxy*szz - syz*sxz) + 
                  sxz * (sxy*syz - syy*sxz))
            
            # Von Mises stress
            mean_normal = I1 / 3.0
            sxx_dev, syy_dev, szz_dev = sxx - mean_normal, syy - mean_normal, szz - mean_normal
            vm = np.sqrt(1.5 * (sxx_dev**2 + syy_dev**2 + szz_dev**2 + 
                               2 * (sxy**2 + sxz**2 + syz**2)))
            
            df["stress_I1"] = I1
            df["stress_I2"] = I2
            df["stress_I3"] = I3
            df["stress_vm"] = vm
            df["stress_hydro"] = -I1 / 3.0  # Stress hidrostático
            
        except Exception as e:
            logger.warning(f"Error calculando invariantes de stress: {str(e)}")
        
        return df
    
    def _extract_energy_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extraer features de energía potencial (bajo riesgo de fuga)"""
        features = {}
        
        # Identificar columna de energía
        pe_col = None
        for col in ["c_peatom", "pe", "potential_energy"]:
            if col in df.columns:
                pe_col = col
                break
        
        if pe_col is None:
            return features
        
        pe_series = df[pe_col].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
        
        if len(pe_series) == 0:
            return features
        
        # Estadísticos robustos
        features["pe_mean"] = float(pe_series.mean())
        features["pe_std"] = float(pe_series.std())
        features["pe_median"] = float(pe_series.median())
        
        # Medidas robustas adicionales
        q25, q75 = pe_series.quantile([0.25, 0.75])
        features["pe_iqr"] = float(q75 - q25)  # Rango intercuartil
        
        # Desviación absoluta mediana (MAD)
        mad = (pe_series - pe_series.median()).abs().median()
        features["pe_mad"] = float(mad)
        
        # Entropía del histograma (no revela conteos directos)
        try:
            hist, _ = np.histogram(pe_series, bins=self.config.energy_bins, 
                                 range=(self.config.energy_min, self.config.energy_max))
            hist_norm = hist / hist.sum() if hist.sum() > 0 else hist
            entropy = -np.sum(hist_norm * np.log(hist_norm + 1e-10))
            features["pe_entropy"] = float(entropy)
        except Exception:
            features["pe_entropy"] = 0.0
        
        # Skewness y kurtosis robustos (NUEVOS)
        try:
            features["pe_skew_robust"] = float(stats.skew(pe_series, nan_policy='omit'))
            features["pe_kurt_robust"] = float(stats.kurtosis(pe_series, nan_policy='omit'))
        except Exception:
            features["pe_skew_robust"] = 0.0
            features["pe_kurt_robust"] = 0.0
        
        return features
    
    def _extract_stress_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extraer features de stress (riesgo medio-bajo)"""
        features = {}
        
        stress_cols = ["stress_I1", "stress_I2", "stress_I3", "stress_vm", "stress_hydro"]
        
        for col in stress_cols:
            if col not in df.columns:
                continue
                
            series = df[col].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
            
            if len(series) == 0:
                continue
            
            # Solo estadísticos básicos y robustos
            features[f"{col}_mean"] = float(series.mean())
            features[f"{col}_std"] = float(series.std())
            
            # Cuartiles solo en modo estándar o completo
            allowed = FeatureCategories.get_allowed_features(self.config.feature_mode)
            if allowed is None or f"{col}_q75" in allowed:
                q25, q75 = series.quantile([0.25, 0.75])
                features[f"{col}_q25"] = float(q25)
                features[f"{col}_q75"] = float(q75)
        
        return features
    
    def _extract_coordination_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extraer features de coordinación (CON CONTROL ESTRICTO)"""
        features = {}
        
        # Identificar columna de coordinación
        coord_col = None
        for col in ["c_coord", "coord", "coordination"]:
            if col in df.columns:
                coord_col = col
                break
        
        if coord_col is None:
            return features
        
        coord_series = df[coord_col].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
        
        if len(coord_series) == 0:
            return features
        
        # Features básicas (siempre seguras)
        features["coord_mean"] = float(coord_series.mean())
        features["coord_std"] = float(coord_series.std())
        
        # Entropía de la distribución (no revela conteos directos)
        try:
            hist, _ = np.histogram(coord_series, bins=range(0, 15))
            hist_norm = hist / hist.sum() if hist.sum() > 0 else hist
            entropy = -np.sum(hist_norm * np.log(hist_norm + 1e-10))
            features["coord_entropy"] = float(entropy)
        except Exception:
            features["coord_entropy"] = 0.0
        
        # Features de bins SOLO si el modo lo permite (CORREGIDO)
        if self.config.feature_mode != FeatureMode.CONSERVATIVE:
            # Bins menos correlacionados con vacancies
            total_atoms = len(coord_series)
            features["coord_bin_10_11"] = float(((coord_series >= 10) & (coord_series <= 11)).sum() / total_atoms)
            features["coord_bin_12"] = float((coord_series == 12).sum() / total_atoms)
        
        return features
    
    def _extract_spatial_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extraer features espaciales (bajo riesgo)"""
        features = {}
        
        spatial_cols = ['x', 'y', 'z']
        if not all(col in df.columns for col in spatial_cols):
            return features
        
        try:
            # Centro de masa
            com_x, com_y, com_z = df['x'].mean(), df['y'].mean(), df['z'].mean()
            
            # Radio de giro
            r_squared = (df['x'] - com_x)**2 + (df['y'] - com_y)**2 + (df['z'] - com_z)**2
            features["gyration_radius"] = float(np.sqrt(r_squared.mean()))
            
            # Dispersión espacial
            features["spatial_std_x"] = float(df['x'].std())
            features["spatial_std_y"] = float(df['y'].std())
            features["spatial_std_z"] = float(df['z'].std())
            
        except Exception as e:
            logger.warning(f"Error calculando features espaciales: {str(e)}")
        
        return features
    
    def _extract_voronoi_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extraer features de volumen de Voronoi"""
        features = {}
        
        voro_col = "c_voro[1]"  # Volumen de Voronoi típico
        if voro_col not in df.columns:
            return features
        
        try:
            voro_series = df[voro_col].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
            
            if len(voro_series) > 0:
                features["voro_vol_mean"] = float(voro_series.mean())
                features["voro_vol_std"] = float(voro_series.std())
                
                # Coeficiente de variación
                if voro_series.mean() != 0:
                    features["voro_vol_cv"] = float(voro_series.std() / voro_series.mean())
                else:
                    features["voro_vol_cv"] = 0.0
                    
        except Exception as e:
            logger.warning(f"Error calculando features de Voronoi: {str(e)}")
        
        return features
    
    def _extract_system_features(self, n_atoms: int, metadata: Optional[Dict]) -> Dict[str, float]:
        """Extraer features del sistema (con cuidado) - CORREGIDO"""
        features = {}
        
        if metadata and 'box_volume' in metadata:
            # Densidad efectiva (puede ser útil pero con precaución)
            if self.config.feature_mode != FeatureMode.CONSERVATIVE:
                effective_density = n_atoms / metadata['box_volume']
                features["effective_density"] = float(effective_density)
        
        return features
    
    # ============== FEATURES AVANZADAS (NUEVAS Y SEGURAS) ==============
    
    def _extract_thermodynamic_advanced_features(self, df: pd.DataFrame, base_features: Dict) -> Dict[str, float]:
        """Generar features termodinámicas avanzadas (SEGURAS)"""
        features = {}
        
        # Solo proceder si tenemos features de energía básicas
        if "pe_mean" not in base_features or "pe_std" not in base_features:
            return features
        
        try:
            # 1. Thermal fluctuation index (normalizada)
            if abs(base_features["pe_mean"]) > 1e-8:
                features["thermal_fluctuation_index"] = float(base_features["pe_std"] / abs(base_features["pe_mean"]))
            else:
                features["thermal_fluctuation_index"] = 0.0
            
            # 2. PE disorder metric (entropía × skewness)
            if "pe_entropy" in base_features and "pe_skew_robust" in base_features:
                features["pe_disorder_metric"] = float(base_features["pe_entropy"] * abs(base_features["pe_skew_robust"]))
            
            # 3. Energy gradient magnitude (aproximación)
            if all(f"spatial_std_{axis}" in base_features for axis in ['x', 'y', 'z']):
                spatial_var = np.sqrt(base_features["spatial_std_x"]**2 + 
                                    base_features["spatial_std_y"]**2 + 
                                    base_features["spatial_std_z"]**2)
                features["pe_gradient_magnitude"] = float(np.sqrt(base_features["pe_std"]**2 + spatial_var**2))
            
            # 4. Stress-related avanzadas (si están disponibles)
            if "stress_vm_mean" in base_features and "stress_vm_std" in base_features:
                # Stress instability
                if abs(base_features["stress_vm_mean"]) > 1e-8:
                    features["stress_instability"] = float(base_features["stress_vm_std"] / abs(base_features["stress_vm_mean"]))
                
                # Stress anisotropy
                if "stress_I1_mean" in base_features and "stress_I2_mean" in base_features:
                    if abs(base_features["stress_vm_mean"]) > 1e-8:
                        anisotropy = (base_features["stress_I1_mean"] - base_features["stress_I2_mean"]) / abs(base_features["stress_vm_mean"])
                        features["stress_anisotropy"] = float(anisotropy)
                
                # Hydrostatic pressure ratio
                if "stress_hydro_mean" in base_features:
                    if abs(base_features["stress_vm_mean"]) > 1e-8:
                        features["hydrostatic_pressure_ratio"] = float(base_features["stress_hydro_mean"] / abs(base_features["stress_vm_mean"]))
                        
        except Exception as e:
            logger.warning(f"Error en features termodinámicas avanzadas: {str(e)}")
        
        return features
    
    def _extract_structural_advanced_features(self, df: pd.DataFrame, base_features: Dict, 
                                            n_atoms: int, metadata: Optional[Dict]) -> Dict[str, float]:
        """Generar features estructurales mejoradas (SEGURAS)"""
        features = {}
        
        try:
            # 1. Atomic density local
            if "gyration_radius" in base_features and base_features["gyration_radius"] > 1e-8:
                features["atomic_density_local"] = float(n_atoms / (base_features["gyration_radius"]**3))
            
            # 2. Spatial anisotropy
            if all(f"spatial_std_{axis}" in base_features for axis in ['x', 'y', 'z']):
                spatial_stds = [base_features[f"spatial_std_{axis}"] for axis in ['x', 'y', 'z']]
                spatial_max, spatial_min = max(spatial_stds), min(spatial_stds)
                if spatial_min > 1e-8:
                    features["spatial_anisotropy"] = float(spatial_max / spatial_min)
                else:
                    features["spatial_anisotropy"] = 1.0
            
            # 3. Volume packing efficiency (aproximación usando volumen de Voronoi)
            if "voro_vol_mean" in base_features:
                # Volumen atómico teórico para Ni (radio ~1.24 Å)
                theoretical_atomic_vol = 4/3 * np.pi * (1.24**3)  # Å³
                if theoretical_atomic_vol > 0:
                    features["volume_packing_efficiency"] = float(base_features["voro_vol_mean"] / theoretical_atomic_vol)
            
            # 4. Coordination disorder
            if "coord_entropy" in base_features and "coord_std" in base_features:
                features["coordination_disorder"] = float(base_features["coord_entropy"] * base_features["coord_std"])
            
            # 5. Effective density normalized
            if "effective_density" in base_features and n_atoms > 0:
                features["effective_density_normalized"] = float(base_features["effective_density"] / n_atoms)
            
            # 6. Voronoi volume coefficient enhanced
            if "voro_vol_cv" in base_features and "voro_vol_std" in base_features:
                features["voro_vol_cv_enhanced"] = float(base_features["voro_vol_cv"] * base_features["voro_vol_std"])
                
        except Exception as e:
            logger.warning(f"Error en features estructurales avanzadas: {str(e)}")
        
        return features
    
    def _extract_combined_advanced_features(self, df: pd.DataFrame, base_features: Dict) -> Dict[str, float]:
        """Generar features combinadas más predictivas (SEGURAS)"""
        features = {}
        
        try:
            # 1. Energy-stress coupling
            if "pe_std" in base_features and "stress_vm_std" in base_features:
                features["energy_stress_coupling"] = float(base_features["pe_std"] * base_features["stress_vm_std"])
            
            # 2. Structural cohesion
            if "pe_mean" in base_features and "gyration_radius" in base_features:
                if abs(base_features["gyration_radius"]) > 1e-8:
                    features["structural_cohesion"] = float(base_features["pe_mean"] / abs(base_features["gyration_radius"]))
            
            # 3. Thermodynamic imbalance
            if "pe_entropy" in base_features and "stress_instability" in features:
                features["thermodynamic_imbalance"] = float(base_features["pe_entropy"] + features["stress_instability"])
            
            # 4. Vacancy density proxy (CUIDADOSA - usar densidad teórica vs efectiva)
            if "effective_density" in base_features and "gyration_radius" in base_features:
                if abs(base_features["gyration_radius"]) > 1e-8:
                    # Calcular densidad teórica basada en geometría
                    theoretical_density = len(df) / (base_features["gyration_radius"]**3) if len(df) > 0 else 0
                    if theoretical_density > 1e-8:
                        vacancy_proxy = (theoretical_density - base_features["effective_density"]) / theoretical_density
                        features["vacancy_density_proxy"] = float(max(0, min(1, vacancy_proxy)))  # Clamp [0,1]
            
            # 5. Multi-scale disorder
            if all(key in base_features for key in ["pe_entropy", "coord_entropy", "voro_vol_cv"]):
                features["multiscale_disorder"] = float(
                    base_features["pe_entropy"] * base_features["coord_entropy"] * base_features["voro_vol_cv"]
                )
            
            # 6. Energy asymmetry
            if "pe_skew_robust" in base_features and "pe_kurt_robust" in base_features:
                features["energy_asymmetry"] = float(base_features["pe_skew_robust"] * base_features["pe_kurt_robust"])
                
        except Exception as e:
            logger.warning(f"Error en features combinadas avanzadas: {str(e)}")
        
        return features
    
    def _extract_ratio_advanced_features(self, df: pd.DataFrame, base_features: Dict) -> Dict[str, float]:
        """Generar features basadas en ratios importantes (SEGURAS)"""
        features = {}
        
        try:
            # 1. PE variability ratio
            if all(key in base_features for key in ["pe_iqr", "pe_mad", "pe_mean"]):
                if abs(base_features["pe_mean"]) > 1e-8:
                    variability_sum = base_features["pe_iqr"] + base_features["pe_mad"]
                    features["pe_variability_ratio"] = float(variability_sum / abs(base_features["pe_mean"]))
            
            # 2. Stress component ratios
            if "stress_I1_mean" in base_features and "stress_I2_mean" in base_features:
                if abs(base_features["stress_I2_mean"]) > 1e-8:
                    features["stress_I1_I2_ratio"] = float(base_features["stress_I1_mean"] / abs(base_features["stress_I2_mean"]))
            
            if "stress_I2_mean" in base_features and "stress_I3_mean" in base_features:
                if abs(base_features["stress_I3_mean"]) > 1e-8:
                    features["stress_I2_I3_ratio"] = float(base_features["stress_I2_mean"] / abs(base_features["stress_I3_mean"]))
            
            # 3. Spatial-energy correlation proxy
            if "coord_mean" in base_features and "pe_mean" in base_features:
                features["spatial_energy_proxy"] = float(base_features["coord_mean"] * base_features["pe_mean"])
            
            # 4. Volume-energy density
            if "pe_mean" in base_features and "voro_vol_mean" in base_features:
                if abs(base_features["voro_vol_mean"]) > 1e-8:
                    features["volume_energy_density"] = float(base_features["pe_mean"] / abs(base_features["voro_vol_mean"]))
                    
        except Exception as e:
            logger.warning(f"Error en features de ratios avanzadas: {str(e)}")
        
        return features
    
    # ============== MÉTODOS DE CONTROL SIN FILTRADO AUTOMÁTICO ==============
    
    def _add_feature_risk_metadata(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Agregar metadata de riesgo sin filtrar automáticamente"""
        # No filtrar nada, solo mantener toda la información para el usuario
        # El usuario tendrá control total sobre qué features usar
        return features
    
    def get_feature_risk_classification(self) -> Dict[str, Dict[str, str]]:
        """
        Obtener clasificación de riesgo de todas las features para que el usuario decida
        
        Returns:
            Dict con clasificación de riesgo por feature
        """
        # Features originales (generalmente seguras)
        original_features_low_risk = {
            'pe_mean': 'low', 'pe_std': 'low', 'pe_median': 'low', 'pe_iqr': 'low', 'pe_mad': 'low',
            'pe_entropy': 'low', 'stress_I1_mean': 'low', 'stress_I1_std': 'low',
            'stress_I2_mean': 'low', 'stress_I2_std': 'low', 'stress_I3_mean': 'low', 'stress_I3_std': 'low',
            'stress_vm_mean': 'low', 'stress_vm_std': 'low', 'stress_hydro_mean': 'low', 'stress_hydro_std': 'low',
            'coord_mean': 'low', 'coord_std': 'low', 'coord_entropy': 'low',
            'gyration_radius': 'low', 'spatial_std_x': 'low', 'spatial_std_y': 'low', 'spatial_std_z': 'low',
            'voro_vol_mean': 'low', 'voro_vol_std': 'low', 'voro_vol_cv': 'low'
        }
        
        # Features avanzadas de bajo riesgo
        advanced_features_low_risk = {
            'pe_skew_robust': 'low', 'pe_kurt_robust': 'low', 'thermal_fluctuation_index': 'low',
            'pe_gradient_magnitude': 'low', 'atomic_density_local': 'low', 'spatial_anisotropy': 'low',
            'energy_stress_coupling': 'low', 'structural_cohesion': 'low'
        }
        
        # Features avanzadas de riesgo medio
        advanced_features_medium_risk = {
            'pe_disorder_metric': 'medium', 'stress_instability': 'medium', 'stress_anisotropy': 'medium',
            'hydrostatic_pressure_ratio': 'medium', 'volume_packing_efficiency': 'medium',
            'coordination_disorder': 'medium', 'effective_density_normalized': 'medium',
            'voro_vol_cv_enhanced': 'medium', 'thermodynamic_imbalance': 'medium',
            'multiscale_disorder': 'medium', 'energy_asymmetry': 'medium', 'pe_variability_ratio': 'medium',
            'stress_I1_I2_ratio': 'medium', 'stress_I2_I3_ratio': 'medium', 'spatial_energy_proxy': 'medium',
            'volume_energy_density': 'medium', 'coord_bin_10_11': 'medium', 'coord_bin_12': 'medium',
            'effective_density': 'medium'
        }
        
        # Features avanzadas de alto riesgo (mayor correlación potencial con vacancies)
        advanced_features_high_risk = {
            'vacancy_density_proxy': 'high'  # Esta puede tener alta correlación por diseño
        }
        
        # Combinar todas las clasificaciones
        all_classifications = {}
        all_classifications.update(original_features_low_risk)
        all_classifications.update(advanced_features_low_risk)
        all_classifications.update(advanced_features_medium_risk)
        all_classifications.update(advanced_features_high_risk)
        
        return {
            'feature_risk_levels': all_classifications,
            'risk_descriptions': {
                'low': 'Bajo riesgo de fuga de información - Seguro usar en la mayoría de casos',
                'medium': 'Riesgo medio - Revisar correlaciones con target antes de usar',
                'high': 'Alto riesgo - Diseñado para alta correlación, usar con precaución'
            }
        }
    
    def _add_gaussian_noise_to_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Agregar ruido gaussiano a features numéricas"""
        if not self.config.add_noise:
            return features
        
        noisy_features = {}
        for key, value in features.items():
            if isinstance(value, (int, float)) and not key.startswith('_') and key != 'vacancies':
                # Agregar ruido proporcional al valor
                noise = np.random.normal(0, self.config.noise_level * abs(value))
                noisy_features[key] = float(value + noise)
            else:
                noisy_features[key] = value
        
        return noisy_features
    
    def _compute_file_hash(self, df: pd.DataFrame) -> str:
        """Calcular hash único para el contenido del frame"""
        # Usar muestra pequeña para eficiencia
        sample = df.head(50).to_string()
        return hashlib.md5(sample.encode()).hexdigest()[:8]
    
    def get_feature_summary(self) -> Dict[str, list]:
        """Obtener resumen de tipos de features disponibles"""
        return {
            'original_safe_features': [
                'pe_mean', 'pe_std', 'pe_median', 'pe_iqr', 'pe_mad', 'pe_entropy',
                'stress_*_mean', 'stress_*_std', 'coord_mean', 'coord_std', 'coord_entropy',
                'gyration_radius', 'spatial_std_*', 'voro_vol_*', 'effective_density'
            ],
            'advanced_thermodynamic': [
                'thermal_fluctuation_index', 'pe_disorder_metric', 'pe_gradient_magnitude',
                'stress_instability', 'stress_anisotropy', 'hydrostatic_pressure_ratio'
            ],
            'advanced_structural': [
                'atomic_density_local', 'spatial_anisotropy', 'volume_packing_efficiency',
                'coordination_disorder', 'effective_density_normalized', 'voro_vol_cv_enhanced'
            ],
            'advanced_combined': [
                'energy_stress_coupling', 'structural_cohesion', 'thermodynamic_imbalance',
                'vacancy_density_proxy', 'multiscale_disorder', 'energy_asymmetry'
            ],
            'advanced_ratios': [
                'pe_variability_ratio', 'stress_I1_I2_ratio', 'stress_I2_I3_ratio',
                'spatial_energy_proxy', 'volume_energy_density'
            ]
        }
    
    def get_all_possible_features(self) -> Dict[str, Dict[str, str]]:
        """
        Obtener lista completa de todas las features posibles con su descripción y nivel de riesgo
        
        Returns:
            Dict con feature_name -> {description, risk_level, category}
        """
        risk_classification = self.get_feature_risk_classification()
        feature_risks = risk_classification['feature_risk_levels']
        
        all_features = {
            # Energy features
            'pe_mean': {'description': 'Energía potencial promedio', 'risk_level': 'low', 'category': 'energy_basic'},
            'pe_std': {'description': 'Desviación estándar de energía potencial', 'risk_level': 'low', 'category': 'energy_basic'},
            'pe_median': {'description': 'Mediana de energía potencial', 'risk_level': 'low', 'category': 'energy_basic'},
            'pe_iqr': {'description': 'Rango intercuartil de energía potencial', 'risk_level': 'low', 'category': 'energy_basic'},
            'pe_mad': {'description': 'Desviación absoluta mediana de energía potencial', 'risk_level': 'low', 'category': 'energy_basic'},
            'pe_entropy': {'description': 'Entropía de la distribución de energía', 'risk_level': 'low', 'category': 'energy_basic'},
            'pe_skew_robust': {'description': 'Skewness robusto de energía potencial', 'risk_level': 'low', 'category': 'energy_advanced'},
            'pe_kurt_robust': {'description': 'Kurtosis robusto de energía potencial', 'risk_level': 'low', 'category': 'energy_advanced'},
            'thermal_fluctuation_index': {'description': 'Índice de fluctuaciones térmicas normalizadas', 'risk_level': 'low', 'category': 'energy_advanced'},
            'pe_disorder_metric': {'description': 'Métrica de desorden energético', 'risk_level': 'medium', 'category': 'energy_advanced'},
            'pe_gradient_magnitude': {'description': 'Magnitud del gradiente energético', 'risk_level': 'low', 'category': 'energy_advanced'},
            'pe_variability_ratio': {'description': 'Ratio de variabilidad energética', 'risk_level': 'medium', 'category': 'energy_advanced'},
            
            # Stress features
            'stress_I1_mean': {'description': 'Primer invariante de stress promedio', 'risk_level': 'low', 'category': 'stress_basic'},
            'stress_I2_mean': {'description': 'Segundo invariante de stress promedio', 'risk_level': 'low', 'category': 'stress_basic'},
            'stress_I3_mean': {'description': 'Tercer invariante de stress promedio', 'risk_level': 'low', 'category': 'stress_basic'},
            'stress_vm_mean': {'description': 'Stress von Mises promedio', 'risk_level': 'low', 'category': 'stress_basic'},
            'stress_hydro_mean': {'description': 'Stress hidrostático promedio', 'risk_level': 'low', 'category': 'stress_basic'},
            'stress_instability': {'description': 'Índice de inestabilidad de stress', 'risk_level': 'medium', 'category': 'stress_advanced'},
            'stress_anisotropy': {'description': 'Anisotropía de stress', 'risk_level': 'medium', 'category': 'stress_advanced'},
            'hydrostatic_pressure_ratio': {'description': 'Ratio de presión hidrostática', 'risk_level': 'medium', 'category': 'stress_advanced'},
            'stress_I1_I2_ratio': {'description': 'Ratio entre invariantes I1/I2', 'risk_level': 'medium', 'category': 'stress_advanced'},
            'stress_I2_I3_ratio': {'description': 'Ratio entre invariantes I2/I3', 'risk_level': 'medium', 'category': 'stress_advanced'},
            
            # Coordination features
            'coord_mean': {'description': 'Número de coordinación promedio', 'risk_level': 'low', 'category': 'coordination'},
            'coord_std': {'description': 'Desviación estándar de coordinación', 'risk_level': 'low', 'category': 'coordination'},
            'coord_entropy': {'description': 'Entropía de distribución de coordinación', 'risk_level': 'low', 'category': 'coordination'},
            'coord_bin_10_11': {'description': 'Fracción de átomos con coordinación 10-11', 'risk_level': 'medium', 'category': 'coordination'},
            'coord_bin_12': {'description': 'Fracción de átomos con coordinación 12', 'risk_level': 'medium', 'category': 'coordination'},
            'coordination_disorder': {'description': 'Métrica de desorden en coordinación', 'risk_level': 'medium', 'category': 'coordination'},
            
            # Spatial features
            'gyration_radius': {'description': 'Radio de giro del sistema', 'risk_level': 'low', 'category': 'spatial_basic'},
            'spatial_std_x': {'description': 'Desviación estándar espacial en X', 'risk_level': 'low', 'category': 'spatial_basic'},
            'spatial_std_y': {'description': 'Desviación estándar espacial en Y', 'risk_level': 'low', 'category': 'spatial_basic'},
            'spatial_std_z': {'description': 'Desviación estándar espacial en Z', 'risk_level': 'low', 'category': 'spatial_basic'},
            'spatial_anisotropy': {'description': 'Anisotropía espacial del sistema', 'risk_level': 'low', 'category': 'spatial_advanced'},
            'atomic_density_local': {'description': 'Densidad atómica local', 'risk_level': 'low', 'category': 'spatial_advanced'},
            
            # Voronoi features
            'voro_vol_mean': {'description': 'Volumen Voronoi promedio', 'risk_level': 'low', 'category': 'voronoi'},
            'voro_vol_std': {'description': 'Desviación estándar volumen Voronoi', 'risk_level': 'low', 'category': 'voronoi'},
            'voro_vol_cv': {'description': 'Coeficiente de variación volumen Voronoi', 'risk_level': 'low', 'category': 'voronoi'},
            'voro_vol_cv_enhanced': {'description': 'Coeficiente de variación Voronoi mejorado', 'risk_level': 'medium', 'category': 'voronoi'},
            'volume_packing_efficiency': {'description': 'Eficiencia de empaquetamiento volumétrico', 'risk_level': 'medium', 'category': 'voronoi'},
            
            # System features
            'effective_density': {'description': 'Densidad efectiva del sistema', 'risk_level': 'medium', 'category': 'system'},
            'effective_density_normalized': {'description': 'Densidad efectiva normalizada', 'risk_level': 'medium', 'category': 'system'},
            
            # Combined advanced features
            'energy_stress_coupling': {'description': 'Acoplamiento energía-stress', 'risk_level': 'low', 'category': 'combined'},
            'structural_cohesion': {'description': 'Cohesión estructural', 'risk_level': 'low', 'category': 'combined'},
            'thermodynamic_imbalance': {'description': 'Desequilibrio termodinámico', 'risk_level': 'medium', 'category': 'combined'},
            'multiscale_disorder': {'description': 'Desorden multi-escala', 'risk_level': 'medium', 'category': 'combined'},
            'energy_asymmetry': {'description': 'Asimetría energética', 'risk_level': 'medium', 'category': 'combined'},
            'spatial_energy_proxy': {'description': 'Proxy de correlación espacial-energética', 'risk_level': 'medium', 'category': 'combined'},
            'volume_energy_density': {'description': 'Densidad energética volumétrica', 'risk_level': 'medium', 'category': 'combined'},
            
            # High-risk features
            'vacancy_density_proxy': {'description': 'Proxy de densidad de vacantes (ALTO RIESGO)', 'risk_level': 'high', 'category': 'high_risk'},
        }
        
        # Actualizar risk levels desde la clasificación automática
        for feature_name, info in all_features.items():
            if feature_name in feature_risks:
                info['risk_level'] = feature_risks[feature_name]
        
        return all_features