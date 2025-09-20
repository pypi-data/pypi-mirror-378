"""
Extractor de features sin fuga de información
Responsabilidad única: calcular features seguras desde datos atómicos
"""

import pandas as pd
import numpy as np
import hashlib
from typing import Dict, Any, Optional
import logging
from .config import ProcessingConfig, FeatureCategories

logger = logging.getLogger(__name__)


class SafeFeatureExtractor:
    """Extractor de features con control estricto de fuga de información"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
    
    def extract_features(self, df: pd.DataFrame, n_atoms: int, 
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extrae features con control de fuga de información
        
        IMPORTANTE: 'vacancies' se calcula como TARGET, NO como feature
        """
        # Agregar invariantes de stress si es posible
        df = self._add_stress_invariants(df)
        
        features = {}
        
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
        
        # 7. CRÍTICO: Calcular TARGET (vacancies) pero NO incluir como feature
        vacancies = int(self.config.atm_total - n_atoms)
        features["vacancies"] = vacancies  # TARGET - será separado del feature set
        
        # 8. Hash para tracking (no es feature de ML)
        features["file_hash"] = self._compute_file_hash(df)
        
        # 9. Filtrar features según modo de seguridad
        features = self._filter_features_by_mode(features)
        
        # 10. Agregar ruido si está configurado
        if self.config.add_noise:
            features = self._add_gaussian_noise_to_features(features)
        
        return features
    
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
            features[f"{col}_median"] = float(series.median())
            
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
        
        # Features de bins SOLO si el modo lo permite
        allowed = FeatureCategories.get_allowed_features(self.config.feature_mode)
        
        if self.config.feature_mode != ProcessingConfig().feature_mode.CONSERVATIVE:
            # Bins menos correlacionados con vacancies
            total_atoms = len(coord_series)
            features["coord_bin_10_11"] = float(((coord_series >= 10) & (coord_series <= 11)).sum() / total_atoms)
            features["coord_bin_12_plus"] = float((coord_series >= 12).sum() / total_atoms)
        
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
            
            # Anisotropía espacial
            std_values = [df[col].std() for col in spatial_cols]
            features["spatial_anisotropy"] = float(max(std_values) / min(std_values)) if min(std_values) > 0 else 1.0
            
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
        """Extraer features del sistema (con cuidado)"""
        features = {}
        
        if metadata and 'box_volume' in metadata:
            # Densidad efectiva (puede ser útil pero con precaución)
            if self.config.feature_mode != ProcessingConfig().feature_mode.CONSERVATIVE:
                effective_density = n_atoms / metadata['box_volume']
                features["effective_density"] = float(effective_density)
        
        return features
    
    def _filter_features_by_mode(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Filtrar features según el modo de seguridad"""
        allowed_features = FeatureCategories.get_allowed_features(self.config.feature_mode)
        
        if allowed_features is None:  # Modo FULL
            return features
        
        # Filtrar solo features permitidas (preservar target y metadata)
        filtered = {}
        for key, value in features.items():
            # Preservar target, metadata y features permitidas
            if (key in ['vacancies', 'file_hash'] or 
                key.startswith('_') or
                key in allowed_features):
                filtered[key] = value
        
        return filtered
    
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