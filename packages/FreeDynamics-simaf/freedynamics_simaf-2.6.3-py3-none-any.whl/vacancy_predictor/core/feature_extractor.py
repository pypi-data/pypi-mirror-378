"""
Extractor de features sin fuga de información - MODIFICADO
Sin filtrado automático - El usuario tiene control total
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
        MODIFICADO: No filtrar automáticamente - usuario tiene control total
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
        
        # 9. MODIFICADO: NO filtrar features automáticamente
        # El usuario tendrá control completo desde la interfaz
        # features = self._filter_features_by_mode(features)  # COMENTADO
        
        # 10. Agregar metadata de riesgo para que el usuario pueda decidir
        features = self._add_feature_risk_metadata(features)
        
        # 11. Agregar ruido solo si está configurado
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
            
            # Estadísticos básicos y robustos
            features[f"{col}_mean"] = float(series.mean())
            features[f"{col}_std"] = float(series.std())
            features[f"{col}_median"] = float(series.median())
            
            # MODIFICADO: Incluir cuartiles sin filtrar por modo
            # El usuario decidirá si usarlas o no
            q25, q75 = series.quantile([0.25, 0.75])
            features[f"{col}_q25"] = float(q25)
            features[f"{col}_q75"] = float(q75)
        
        return features
    
    def _extract_coordination_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extraer features de coordinación (TODAS DISPONIBLES)"""
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
        
        # MODIFICADO: Incluir TODAS las features de bins para que el usuario decida
        total_atoms = len(coord_series)
        
        # Features de coordinación específicas (pueden tener diferentes niveles de riesgo)
        features["coord_below_8"] = float((coord_series < 8).sum() / total_atoms)
        features["coord_bin_8_9"] = float(((coord_series >= 8) & (coord_series < 10)).sum() / total_atoms)
        features["coord_bin_10_11"] = float(((coord_series >= 10) & (coord_series <= 11)).sum() / total_atoms)
        features["coord_bin_12_plus"] = float((coord_series >= 12).sum() / total_atoms)
        features["coord_perfect_12"] = float((coord_series == 12).sum() / total_atoms)
        
        # Fracciones para diferentes umbrales
        for threshold in [9, 10, 11]:
            features[f"frac_coord_le_{threshold}"] = float((coord_series <= threshold).sum() / total_atoms)
        
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
            
            # Centro de masa normalizado
            features["com_x_norm"] = float(com_x)
            features["com_y_norm"] = float(com_y)
            features["com_z_norm"] = float(com_z)
            
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
                features["voro_vol_median"] = float(voro_series.median())
                
                # Coeficiente de variación
                if voro_series.mean() != 0:
                    features["voro_vol_cv"] = float(voro_series.std() / voro_series.mean())
                else:
                    features["voro_vol_cv"] = 0.0
                
                # Cuartiles
                q25, q75 = voro_series.quantile([0.25, 0.75])
                features["voro_vol_q25"] = float(q25)
                features["voro_vol_q75"] = float(q75)
                    
        except Exception as e:
            logger.warning(f"Error calculando features de Voronoi: {str(e)}")
        
        return features
    
    def _extract_system_features(self, n_atoms: int, metadata: Optional[Dict]) -> Dict[str, float]:
        """Extraer features del sistema (TODAS DISPONIBLES)"""
        features = {}
        
        # MODIFICADO: Incluir todas las features de sistema para que el usuario decida
        if metadata and 'box_volume' in metadata:
            # Densidad efectiva
            effective_density = n_atoms / metadata['box_volume']
            features["effective_density"] = float(effective_density)
            
            # Número de átomos normalizado (puede ser útil)
            features["n_atoms_normalized"] = float(n_atoms / self.config.atm_total)
            
            # Features de volumen
            features["box_volume"] = float(metadata['box_volume'])
        
        # Features potencialmente riesgosas pero disponibles para decisión del usuario
        features["n_atoms_direct"] = float(n_atoms)  # RIESGO ALTO - pero disponible
        
        return features
    
    def _add_feature_risk_metadata(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Agregar metadata de riesgo sin filtrar automáticamente"""
        # MODIFICADO: Solo agregar info de riesgo, no filtrar
        risk_levels = self._get_feature_risk_levels()
        
        # Agregar metadata de riesgo como información, no como filtro
        features["_feature_risk_info"] = {
            feature: risk_levels.get(feature, 'unknown') 
            for feature in features.keys()
            if not feature.startswith('_') and feature not in ['vacancies', 'file_hash']
        }
        
        return features
    
    def _get_feature_risk_levels(self) -> Dict[str, str]:
        """Obtener niveles de riesgo de features para información del usuario"""
        return {
            # Bajo riesgo
            'pe_mean': 'low', 'pe_std': 'low', 'pe_median': 'low', 'pe_iqr': 'low', 'pe_mad': 'low',
            'pe_entropy': 'low',
            'stress_I1_mean': 'low', 'stress_I1_std': 'low', 'stress_I1_median': 'low',
            'stress_I2_mean': 'low', 'stress_I2_std': 'low', 'stress_I2_median': 'low',
            'stress_I3_mean': 'low', 'stress_I3_std': 'low', 'stress_I3_median': 'low',
            'stress_vm_mean': 'low', 'stress_vm_std': 'low', 'stress_vm_median': 'low',
            'stress_hydro_mean': 'low', 'stress_hydro_std': 'low', 'stress_hydro_median': 'low',
            'coord_mean': 'low', 'coord_std': 'low', 'coord_entropy': 'low',
            'gyration_radius': 'low', 'spatial_std_x': 'low', 'spatial_std_y': 'low', 'spatial_std_z': 'low',
            'spatial_anisotropy': 'low',
            'voro_vol_mean': 'low', 'voro_vol_std': 'low', 'voro_vol_median': 'low', 'voro_vol_cv': 'low',
            'com_x_norm': 'low', 'com_y_norm': 'low', 'com_z_norm': 'low',
            
            # Riesgo medio
            'stress_I1_q25': 'medium', 'stress_I1_q75': 'medium',
            'stress_I2_q25': 'medium', 'stress_I2_q75': 'medium',
            'stress_I3_q25': 'medium', 'stress_I3_q75': 'medium',
            'stress_vm_q25': 'medium', 'stress_vm_q75': 'medium',
            'stress_hydro_q25': 'medium', 'stress_hydro_q75': 'medium',
            'coord_bin_8_9': 'medium', 'coord_bin_10_11': 'medium', 'coord_bin_12_plus': 'medium',
            'effective_density': 'medium', 'box_volume': 'medium',
            'voro_vol_q25': 'medium', 'voro_vol_q75': 'medium',
            
            # Alto riesgo - directamente correlacionado con vacancies
            'coord_below_8': 'high', 'coord_perfect_12': 'high',
            'frac_coord_le_9': 'high', 'frac_coord_le_10': 'high', 'frac_coord_le_11': 'high',
            'n_atoms_normalized': 'high', 'n_atoms_direct': 'critical'
        }
    
    # COMENTADO: El método de filtrado automático ya no se usa
    # def _filter_features_by_mode(self, features: Dict[str, Any]) -> Dict[str, Any]:
    #     """Filtrar features según el modo de seguridad - DESACTIVADO"""
    #     return features
    
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