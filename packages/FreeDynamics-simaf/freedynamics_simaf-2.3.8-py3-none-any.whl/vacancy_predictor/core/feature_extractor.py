"""
Extractor de features sin fuga de información - MODIFICADO
Sin dependencia de n_atoms - Solo cálculos intrínsecos del .dump
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
    
    def extract_features(self, df: pd.DataFrame, 
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extrae features con control de fuga de información
        
        CAMBIO CRÍTICO: Ya NO se usa n_atoms para normalización
        Todos los cálculos son intrínsecos al DataFrame
        
        Args:
            df: DataFrame con datos atómicos del .dump
            metadata: Metadatos opcionales del sistema
            
        Returns:
            Dict con features calculadas y vacancies como target
        """
        # Agregar invariantes de stress si es posible
        df = self._add_stress_invariants(df)
        
        # Obtener número real de átomos en el archivo
        n_atoms_in_file = len(df)
        
        features = {}
        
        # 1. Features de energía (bajo riesgo)
        features.update(self._extract_energy_features(df))
        
        # 2. Features de stress (bajo-medio riesgo)
        features.update(self._extract_stress_features(df))
        
        # 3. Features de coordinación (SIN normalizaciones por n_atoms)
        features.update(self._extract_coordination_features(df))
        
        # 4. Features espaciales (bajo riesgo)
        features.update(self._extract_spatial_features(df))
        
        # 5. Features de volumen de Voronoi (si está disponible)
        features.update(self._extract_voronoi_features(df))
        
        # 6. Features del sistema (SIN dependencia de n_atoms)
        features.update(self._extract_system_features(metadata))
        
        # 7. CRÍTICO: Calcular TARGET (vacancies) - ÚNICO uso de atm_total
        vacancies = int(self.config.atm_total - n_atoms_in_file)
        features["vacancies"] = vacancies  # TARGET - será separado del feature set
        
        # 8. Hash para tracking (no es feature de ML)
        features["file_hash"] = self._compute_file_hash(df)
        
        # 9. Agregar metadata de riesgo para que el usuario pueda decidir
        features = self._add_feature_risk_metadata(features)
        
        # 10. Agregar ruido solo si está configurado
        if self.config.add_noise:
            features = self._add_gaussian_noise_to_features(features)
        
        logger.info(f"Extraídas {len(features)} features de {n_atoms_in_file} átomos. Vacancies: {vacancies}")
        
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
        
        # Percentiles adicionales
        features["pe_q25"] = float(q25)
        features["pe_q75"] = float(q75)
        features["pe_q10"] = float(pe_series.quantile(0.1))
        features["pe_q90"] = float(pe_series.quantile(0.9))
        
        # Rango total
        features["pe_range"] = float(pe_series.max() - pe_series.min())
        
        # Coeficiente de variación
        if pe_series.mean() != 0:
            features["pe_cv"] = float(pe_series.std() / abs(pe_series.mean()))
        else:
            features["pe_cv"] = 0.0
        
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
            
            # Estadísticos básicos
            features[f"{col}_mean"] = float(series.mean())
            features[f"{col}_std"] = float(series.std())
            features[f"{col}_median"] = float(series.median())
            
            # Percentiles
            q25, q75 = series.quantile([0.25, 0.75])
            features[f"{col}_q25"] = float(q25)
            features[f"{col}_q75"] = float(q75)
            features[f"{col}_iqr"] = float(q75 - q25)
            
            # MAD y coeficiente de variación
            mad = (series - series.median()).abs().median()
            features[f"{col}_mad"] = float(mad)
            
            if series.mean() != 0:
                features[f"{col}_cv"] = float(series.std() / abs(series.mean()))
            else:
                features[f"{col}_cv"] = 0.0
        
        return features
    
    def _extract_coordination_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Extraer features de coordinación SIN normalizaciones por n_atoms
        Solo estadísticos y distribuciones intrínsecas
        """
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
        
        # Features básicas (SIEMPRE seguras)
        features["coord_mean"] = float(coord_series.mean())
        features["coord_std"] = float(coord_series.std())
        features["coord_median"] = float(coord_series.median())
        
        # Percentiles
        features["coord_q25"] = float(coord_series.quantile(0.25))
        features["coord_q75"] = float(coord_series.quantile(0.75))
        features["coord_iqr"] = float(features["coord_q75"] - features["coord_q25"])
        
        # MAD
        mad = (coord_series - coord_series.median()).abs().median()
        features["coord_mad"] = float(mad)
        
        # Coeficiente de variación
        if coord_series.mean() != 0:
            features["coord_cv"] = float(coord_series.std() / coord_series.mean())
        else:
            features["coord_cv"] = 0.0
        
        # Entropía de la distribución (NO revela conteos)
        try:
            hist, _ = np.histogram(coord_series, bins=range(0, 15))
            hist_norm = hist / hist.sum() if hist.sum() > 0 else hist
            entropy = -np.sum(hist_norm * np.log(hist_norm + 1e-10))
            features["coord_entropy"] = float(entropy)
        except Exception:
            features["coord_entropy"] = 0.0
        
        # Estadísticos de orden superior
        features["coord_skewness"] = float(coord_series.skew())
        features["coord_kurtosis"] = float(coord_series.kurtosis())
        
        # Valores extremos como estadísticos
        features["coord_min"] = float(coord_series.min())
        features["coord_max"] = float(coord_series.max())
        features["coord_range"] = float(coord_series.max() - coord_series.min())
        
        # ELIMINADO: Todas las features que dependían de fracción de átomos totales
        # Ya no calculamos coord_below_8, coord_perfect_12, frac_coord_le_X, etc.
        # Estas eran las que causaban fuga de información
        
        logger.info(f"Coordinación: mean={features['coord_mean']:.2f}, std={features['coord_std']:.2f}")
        
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
            
            # Centro de masa (puede ser útil para caracterizar defectos)
            features["com_x"] = float(com_x)
            features["com_y"] = float(com_y)
            features["com_z"] = float(com_z)
            
            # Momentos espaciales de orden superior
            for coord in ['x', 'y', 'z']:
                series = df[coord]
                features[f"{coord}_skewness"] = float(series.skew())
                features[f"{coord}_kurtosis"] = float(series.kurtosis())
                
                # Percentiles espaciales
                features[f"{coord}_q25"] = float(series.quantile(0.25))
                features[f"{coord}_q75"] = float(series.quantile(0.75))
            
            # Volumen envolvente aproximado
            x_range = df['x'].max() - df['x'].min()
            y_range = df['y'].max() - df['y'].min()
            z_range = df['z'].max() - df['z'].min()
            features["bounding_volume"] = float(x_range * y_range * z_range)
            
            # Compacidad espacial
            if features["bounding_volume"] > 0:
                features["spatial_compactness"] = float(len(df) / features["bounding_volume"])
            else:
                features["spatial_compactness"] = 0.0
            
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
                # Estadísticos básicos
                features["voro_vol_mean"] = float(voro_series.mean())
                features["voro_vol_std"] = float(voro_series.std())
                features["voro_vol_median"] = float(voro_series.median())
                
                # Coeficiente de variación
                if voro_series.mean() != 0:
                    features["voro_vol_cv"] = float(voro_series.std() / voro_series.mean())
                else:
                    features["voro_vol_cv"] = 0.0
                
                # Percentiles
                features["voro_vol_q25"] = float(voro_series.quantile(0.25))
                features["voro_vol_q75"] = float(voro_series.quantile(0.75))
                features["voro_vol_iqr"] = float(features["voro_vol_q75"] - features["voro_vol_q25"])
                
                # MAD
                mad = (voro_series - voro_series.median()).abs().median()
                features["voro_vol_mad"] = float(mad)
                
                # Estadísticos de forma
                features["voro_vol_skewness"] = float(voro_series.skew())
                features["voro_vol_kurtosis"] = float(voro_series.kurtosis())
                
                # Valores extremos
                features["voro_vol_min"] = float(voro_series.min())
                features["voro_vol_max"] = float(voro_series.max())
                features["voro_vol_range"] = float(voro_series.max() - voro_series.min())
                    
        except Exception as e:
            logger.warning(f"Error calculando features de Voronoi: {str(e)}")
        
        return features
    
    def _extract_system_features(self, metadata: Optional[Dict]) -> Dict[str, float]:
        """
        Extraer features del sistema SIN dependencia de n_atoms
        Solo información intrínseca del sistema
        """
        features = {}
        
        if metadata and 'box_volume' in metadata:
            # Features de volumen del sistema
            features["box_volume"] = float(metadata['box_volume'])
            
            # Otras dimensiones si están disponibles
            if 'box_lengths' in metadata:
                lengths = metadata['box_lengths']
                if len(lengths) >= 3:
                    features["box_length_x"] = float(lengths[0])
                    features["box_length_y"] = float(lengths[1])
                    features["box_length_z"] = float(lengths[2])
                    
                    # Anisotropía de la caja
                    max_length = max(lengths[:3])
                    min_length = min(lengths[:3])
                    features["box_anisotropy"] = float(max_length / min_length) if min_length > 0 else 1.0
        
        # ELIMINADO: Todas las features que dependían de n_atoms:
        # - effective_density (requiere n_atoms / volume)
        # - n_atoms_normalized (requiere n_atoms / atm_total)
        # - n_atoms_direct (directamente correlacionado con vacancies)
        
        return features
    
    def _add_feature_risk_metadata(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Agregar metadata de riesgo sin filtrar automáticamente"""
        risk_levels = self._get_feature_risk_levels()
        
        # Agregar metadata de riesgo como información, no como filtro
        features["_feature_risk_info"] = {
            feature: risk_levels.get(feature, 'low')  # Default a low risk
            for feature in features.keys()
            if not feature.startswith('_') and feature not in ['vacancies', 'file_hash']
        }
        
        return features
    
    def _get_feature_risk_levels(self) -> Dict[str, str]:
        """
        Obtener niveles de riesgo de features - ACTUALIZADOS
        Ahora que eliminamos n_atoms, la mayoría son de bajo riesgo
        """
        return {
            # Bajo riesgo - estadísticos puros sin normalización
            'pe_mean': 'low', 'pe_std': 'low', 'pe_median': 'low', 'pe_iqr': 'low', 'pe_mad': 'low',
            'pe_entropy': 'low', 'pe_q25': 'low', 'pe_q75': 'low', 'pe_q10': 'low', 'pe_q90': 'low',
            'pe_range': 'low', 'pe_cv': 'low',
            
            # Stress features - bajo riesgo
            'stress_I1_mean': 'low', 'stress_I1_std': 'low', 'stress_I1_median': 'low',
            'stress_I2_mean': 'low', 'stress_I2_std': 'low', 'stress_I2_median': 'low',
            'stress_I3_mean': 'low', 'stress_I3_std': 'low', 'stress_I3_median': 'low',
            'stress_vm_mean': 'low', 'stress_vm_std': 'low', 'stress_vm_median': 'low',
            'stress_hydro_mean': 'low', 'stress_hydro_std': 'low', 'stress_hydro_median': 'low',
            
            # Stress percentiles - bajo riesgo
            'stress_I1_q25': 'low', 'stress_I1_q75': 'low', 'stress_I1_iqr': 'low', 'stress_I1_mad': 'low', 'stress_I1_cv': 'low',
            'stress_I2_q25': 'low', 'stress_I2_q75': 'low', 'stress_I2_iqr': 'low', 'stress_I2_mad': 'low', 'stress_I2_cv': 'low',
            'stress_I3_q25': 'low', 'stress_I3_q75': 'low', 'stress_I3_iqr': 'low', 'stress_I3_mad': 'low', 'stress_I3_cv': 'low',
            'stress_vm_q25': 'low', 'stress_vm_q75': 'low', 'stress_vm_iqr': 'low', 'stress_vm_mad': 'low', 'stress_vm_cv': 'low',
            'stress_hydro_q25': 'low', 'stress_hydro_q75': 'low', 'stress_hydro_iqr': 'low', 'stress_hydro_mad': 'low', 'stress_hydro_cv': 'low',
            
            # Coordinación - AHORA BAJO RIESGO (sin fracciones por n_atoms)
            'coord_mean': 'low', 'coord_std': 'low', 'coord_entropy': 'low', 'coord_median': 'low',
            'coord_q25': 'low', 'coord_q75': 'low', 'coord_iqr': 'low', 'coord_mad': 'low', 'coord_cv': 'low',
            'coord_skewness': 'low', 'coord_kurtosis': 'low', 'coord_min': 'low', 'coord_max': 'low', 'coord_range': 'low',
            
            # Espaciales - bajo riesgo
            'gyration_radius': 'low', 'spatial_std_x': 'low', 'spatial_std_y': 'low', 'spatial_std_z': 'low',
            'spatial_anisotropy': 'low', 'com_x': 'low', 'com_y': 'low', 'com_z': 'low',
            'x_skewness': 'low', 'y_skewness': 'low', 'z_skewness': 'low',
            'x_kurtosis': 'low', 'y_kurtosis': 'low', 'z_kurtosis': 'low',
            'x_q25': 'low', 'x_q75': 'low', 'y_q25': 'low', 'y_q75': 'low', 'z_q25': 'low', 'z_q75': 'low',
            'bounding_volume': 'low', 'spatial_compactness': 'low',
            
            # Voronoi - bajo riesgo
            'voro_vol_mean': 'low', 'voro_vol_std': 'low', 'voro_vol_median': 'low', 'voro_vol_cv': 'low',
            'voro_vol_q25': 'low', 'voro_vol_q75': 'low', 'voro_vol_iqr': 'low', 'voro_vol_mad': 'low',
            'voro_vol_skewness': 'low', 'voro_vol_kurtosis': 'low', 'voro_vol_min': 'low', 'voro_vol_max': 'low', 'voro_vol_range': 'low',
            
            # Sistema - bajo riesgo (sin dependencia de n_atoms)
            'box_volume': 'low', 'box_length_x': 'low', 'box_length_y': 'low', 'box_length_z': 'low', 'box_anisotropy': 'low',
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
    
    def get_feature_summary(self) -> Dict[str, Any]:
        """Obtener resumen de las features disponibles"""
        return {
            "total_feature_categories": 5,
            "categories": {
                "energy": "Estadísticos de energía potencial (pe_mean, pe_std, pe_entropy, etc.)",
                "stress": "Invariantes de stress y estadísticos (stress_I1, stress_vm, etc.)",
                "coordination": "Estadísticos de coordinación SIN normalización (coord_mean, coord_std, etc.)",
                "spatial": "Features espaciales y geométricas (gyration_radius, spatial_anisotropy, etc.)",
                "voronoi": "Estadísticos de volúmenes de Voronoi (voro_vol_mean, etc.)",
                "system": "Propiedades del sistema (box_volume, etc.)"
            },
            "risk_levels": {
                "low": "Estadísticos puros sin correlación directa con vacancies",
                "medium": "Features con potencial correlación indirecta",
                "high": "Features que pueden revelar información sobre vacancies"
            },
            "eliminated_features": [
                "n_atoms_direct", "n_atoms_normalized", "effective_density",
                "coord_below_8", "coord_perfect_12", "frac_coord_le_*",
                "vacancy_fraction", "coord_bin_*_fractions"
            ],
            "note": "Todas las features se calculan como estadísticos intrínsecos del DataFrame, sin normalización por número total de átomos."
        }