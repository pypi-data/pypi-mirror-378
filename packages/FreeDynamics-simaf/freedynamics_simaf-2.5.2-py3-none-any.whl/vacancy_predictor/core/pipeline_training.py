"""
Procesador Unificado de Entrenamiento
Combina filtrado de superficie con extracción de features
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import hashlib

from ovito.io import import_file, export_file
from ovito.modifiers import (
    ConstructSurfaceModifier,
    InvertSelectionModifier,
    DeleteSelectedModifier,
    AffineTransformationModifier
)

logger = logging.getLogger(__name__)


class UnifiedTrainingProcessor:
    """
    Procesador unificado que combina:
    1. Filtrado de superficie para quedarse con átomos alrededor del nanoporo
    2. Extracción de features de esos átomos filtrados
    3. Cálculo de vacancies y export a CSV
    """
    
    def __init__(
        self,
        atm_total: int,
        radius: float,
        smoothing_level: int = 0,
        stress_tensor: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        energy_min: float = -4.0,
        energy_max: float = -3.0,
        energy_bins: int = 10,
        output_dir: str = "outputs",
        json_params_path: Optional[str] = None
    ):
        """
        Args:
            atm_total: Número total de átomos en cristal perfecto
            radius: Radio para ConstructSurfaceModifier
            smoothing_level: Nivel de suavizado para ConstructSurfaceModifier
            stress_tensor: Tupla de 3 floats para deformación afín
            energy_min/max: Rango de energía para histogramas
            energy_bins: Número de bins para histogramas
            output_dir: Directorio base de salida
            json_params_path: Ruta al archivo de parámetros (opcional)
        """
        self.atm_total = atm_total
        self.radius = radius
        self.smoothing_level = smoothing_level
        self.stress_tensor = stress_tensor
        self.energy_min = energy_min
        self.energy_max = energy_max
        self.energy_bins = energy_bins
        
        # Configurar directorios
        self.output_dir = Path(output_dir)
        self.output_dir_csv = self.output_dir / "csv"
        self.output_dir_dump = self.output_dir / "dump"
        
        # Crear directorios
        self.output_dir_csv.mkdir(parents=True, exist_ok=True)
        self.output_dir_dump.mkdir(parents=True, exist_ok=True)
        
        # Cargar parámetros adicionales si se proporciona archivo JSON
        if json_params_path and os.path.exists(json_params_path):
            self._load_json_params(json_params_path)
    
    def _load_json_params(self, json_path: str):
        """Cargar parámetros adicionales desde archivo JSON"""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                params = json.load(f)
            
            if "CONFIG" in params and len(params["CONFIG"]) > 0:
                config = params["CONFIG"][0]
                # Actualizar parámetros si están en el JSON
                self.radius = config.get("radius", self.radius)
                self.smoothing_level = config.get("smoothing_level_training", self.smoothing_level)
                self.stress_tensor = tuple(config.get("strees", self.stress_tensor))
                
                logger.info(f"Parámetros cargados desde {json_path}")
        except Exception as e:
            logger.warning(f"No se pudieron cargar parámetros desde {json_path}: {e}")
    
    def process_dump_file(self, dump_file_path: str, apply_stress: bool = False) -> Dict[str, Any]:
        """
        Procesar un archivo .dump individual:
        1. Leer y calcular vacancies
        2. Aplicar filtro de superficie
        3. Extraer features de átomos filtrados
        
        Args:
            dump_file_path: Ruta al archivo .dump
            apply_stress: Si aplicar deformación afín
            
        Returns:
            Dict con features y vacancies
        """
        logger.info(f"Procesando archivo: {dump_file_path}")
        
        # 1. Cargar archivo y obtener número de átomos original
        pipeline = import_file(dump_file_path)
        original_data = pipeline.compute()
        n_atoms_original = original_data.particles.count
        
        # 2. Calcular vacancies
        vacancies = self.atm_total - n_atoms_original
        logger.info(f"Átomos en archivo: {n_atoms_original}, Vacancies calculadas: {vacancies}")
        
        # 3. Aplicar deformación afín si se solicita
        if apply_stress:
            pipeline.modifiers.append(AffineTransformationModifier(
                operate_on={'particles', 'cell'},
                transformation=[
                    [self.stress_tensor[0], 0, 0, 0],
                    [0, self.stress_tensor[1], 0, 0],
                    [0, 0, self.stress_tensor[2], 0]
                ]
            ))
        
        # 4. Aplicar filtro de superficie
        # Primero ConstructSurfaceModifier para identificar superficie
        pipeline.modifiers.append(ConstructSurfaceModifier(
            radius=self.radius,
            smoothing_level=self.smoothing_level,
            identify_regions=True,
            select_surface_particles=True
        ))
        
        # 5. Invertir selección para quedarse con átomos del interior (nanoporo)
        pipeline.modifiers.append(InvertSelectionModifier())
        
        # 6. Eliminar átomos seleccionados (superficie), quedarse con región nanoporo
        pipeline.modifiers.append(DeleteSelectedModifier())
        
        # 7. Obtener datos filtrados
        filtered_data = pipeline.compute()
        n_atoms_filtered = filtered_data.particles.count
        
        logger.info(f"Átomos después del filtro de superficie: {n_atoms_filtered}")
        
        # 8. Convertir a DataFrame para extracción de features
        df_filtered = self._ovito_data_to_dataframe(filtered_data)
        
        # 9. Extraer features de los datos filtrados
        features = self._extract_features(df_filtered, {
            'n_atoms_original': n_atoms_original,
            'n_atoms_filtered': n_atoms_filtered,
            'file_path': dump_file_path
        })
        
        # 10. Añadir vacancies como target
        features['vacancies'] = vacancies
        
        # 11. Opcional: Exportar dump filtrado para verificación
        filtered_dump_path = self.output_dir_dump / f"filtered_{Path(dump_file_path).stem}.dump"
        try:
            export_file(
                pipeline,
                str(filtered_dump_path),
                "lammps/dump",
                columns=[
                    "Particle Identifier",
                    "Particle Type", 
                    "Position.X",
                    "Position.Y",
                    "Position.Z"
                ]
            )
            logger.debug(f"Dump filtrado guardado en: {filtered_dump_path}")
        except Exception as e:
            logger.warning(f"No se pudo exportar dump filtrado: {e}")
        
        # 12. Limpiar pipeline
        pipeline.modifiers.clear()
        
        return features
    
    def _ovito_data_to_dataframe(self, data) -> pd.DataFrame:
        """Convertir datos de OVITO a DataFrame de pandas"""
        df_dict = {}
        
        # Posiciones
        positions = data.particles.positions
        df_dict['x'] = positions[:, 0]
        df_dict['y'] = positions[:, 1] 
        df_dict['z'] = positions[:, 2]
        
        # Otras propiedades disponibles
        for prop_name in data.particles.keys():
            try:
                prop_data = data.particles[prop_name]
                if len(prop_data.shape) == 1:  # Propiedades escalares
                    df_dict[prop_name] = prop_data[:]
                elif len(prop_data.shape) == 2 and prop_data.shape[1] <= 6:  # Tensores pequeños
                    for i in range(prop_data.shape[1]):
                        df_dict[f"{prop_name}[{i+1}]"] = prop_data[:, i]
            except Exception as e:
                logger.debug(f"No se pudo extraer propiedad {prop_name}: {e}")
        
        return pd.DataFrame(df_dict)
    
    def _extract_features(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extraer features del DataFrame filtrado
        Adaptado del SafeFeatureExtractor pero simplificado
        """
        features = {}
        
        # 1. Features de energía potencial
        features.update(self._extract_energy_features(df))
        
        # 2. Features de stress (si están disponibles)
        features.update(self._extract_stress_features(df))
        
        # 3. Features de coordinación (si están disponibles)
        features.update(self._extract_coordination_features(df))
        
        # 4. Features espaciales
        features.update(self._extract_spatial_features(df))
        
        # 5. Features de volumen de Voronoi (si están disponibles)
        features.update(self._extract_voronoi_features(df))
        
        # 6. Features del sistema filtrado
        features.update(self._extract_system_features(df, metadata))
        
        # 7. Hash del archivo para tracking
        features['file_hash'] = self._compute_file_hash(df)
        
        # 8. Metadata del procesamiento
        features['_n_atoms_original'] = metadata['n_atoms_original']
        features['_n_atoms_filtered'] = metadata['n_atoms_filtered']
        features['_filter_ratio'] = metadata['n_atoms_filtered'] / metadata['n_atoms_original']
        
        return features
    
    def _extract_energy_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extraer features de energía potencial"""
        features = {}
        
        # Buscar columna de energía
        energy_cols = ["c_peatom", "pe", "potential_energy", "c_peatom[1]"]
        pe_col = None
        for col in energy_cols:
            if col in df.columns:
                pe_col = col
                break
        
        if pe_col is None:
            return features
        
        pe_series = df[pe_col].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
        
        if len(pe_series) == 0:
            return features
        
        # Estadísticos básicos
        features["pe_mean"] = float(pe_series.mean())
        features["pe_std"] = float(pe_series.std())
        features["pe_median"] = float(pe_series.median())
        features["pe_min"] = float(pe_series.min())
        features["pe_max"] = float(pe_series.max())
        features["pe_range"] = float(pe_series.max() - pe_series.min())
        
        # Percentiles
        features["pe_q25"] = float(pe_series.quantile(0.25))
        features["pe_q75"] = float(pe_series.quantile(0.75))
        features["pe_iqr"] = float(features["pe_q75"] - features["pe_q25"])
        
        # Medidas robustas
        features["pe_mad"] = float((pe_series - pe_series.median()).abs().median())
        
        if pe_series.mean() != 0:
            features["pe_cv"] = float(pe_series.std() / abs(pe_series.mean()))
        else:
            features["pe_cv"] = 0.0
        
        # Estadísticos de forma
        features["pe_skewness"] = float(pe_series.skew())
        features["pe_kurtosis"] = float(pe_series.kurtosis())
        
        # Entropía del histograma
        try:
            hist, _ = np.histogram(pe_series, bins=self.energy_bins, 
                                 range=(self.energy_min, self.energy_max))
            hist_norm = hist / hist.sum() if hist.sum() > 0 else hist
            entropy = -np.sum(hist_norm * np.log(hist_norm + 1e-10))
            features["pe_entropy"] = float(entropy)
        except Exception:
            features["pe_entropy"] = 0.0
        
        return features
    
    def _extract_stress_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extraer features de stress si están disponibles"""
        features = {}
        
        # Buscar componentes del tensor de stress
        stress_cols = [f"c_satom[{i}]" for i in range(1, 7)]
        
        if not all(col in df.columns for col in stress_cols):
            return features
        
        try:
            # Calcular invariantes de stress
            sxx, syy, szz, sxy, sxz, syz = (df[col].astype(float) for col in stress_cols)
            
            # Primer invariante (traza)
            I1 = sxx + syy + szz
            
            # Von Mises stress
            mean_normal = I1 / 3.0
            sxx_dev, syy_dev, szz_dev = sxx - mean_normal, syy - mean_normal, szz - mean_normal
            vm = np.sqrt(1.5 * (sxx_dev**2 + syy_dev**2 + szz_dev**2 + 
                               2 * (sxy**2 + sxz**2 + syz**2)))
            
            # Features de stress hidrostático
            hydro = -I1 / 3.0
            features["stress_hydro_mean"] = float(hydro.mean())
            features["stress_hydro_std"] = float(hydro.std())
            features["stress_hydro_median"] = float(hydro.median())
            
            # Features de Von Mises
            features["stress_vm_mean"] = float(vm.mean())
            features["stress_vm_std"] = float(vm.std())
            features["stress_vm_median"] = float(vm.median())
            features["stress_vm_max"] = float(vm.max())
            
        except Exception as e:
            logger.warning(f"Error calculando features de stress: {e}")
        
        return features
    
    def _extract_coordination_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extraer features de coordinación si están disponibles"""
        features = {}
        
        coord_cols = ["c_coord", "coord", "coordination", "c_coord[1]"]
        coord_col = None
        for col in coord_cols:
            if col in df.columns:
                coord_col = col
                break
        
        if coord_col is None:
            return features
        
        coord_series = df[coord_col].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
        
        if len(coord_series) == 0:
            return features
        
        # Estadísticos básicos
        features["coord_mean"] = float(coord_series.mean())
        features["coord_std"] = float(coord_series.std())
        features["coord_median"] = float(coord_series.median())
        features["coord_min"] = float(coord_series.min())
        features["coord_max"] = float(coord_series.max())
        
        # Percentiles
        features["coord_q25"] = float(coord_series.quantile(0.25))
        features["coord_q75"] = float(coord_series.quantile(0.75))
        features["coord_iqr"] = float(features["coord_q75"] - features["coord_q25"])
        
        # MAD y CV
        features["coord_mad"] = float((coord_series - coord_series.median()).abs().median())
        if coord_series.mean() != 0:
            features["coord_cv"] = float(coord_series.std() / coord_series.mean())
        else:
            features["coord_cv"] = 0.0
        
        # Estadísticos de forma
        features["coord_skewness"] = float(coord_series.skew())
        features["coord_kurtosis"] = float(coord_series.kurtosis())
        
        return features
    
    def _extract_spatial_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extraer features espaciales"""
        features = {}
        
        if not all(col in df.columns for col in ['x', 'y', 'z']):
            return features
        
        try:
            # Centro de masa
            com_x, com_y, com_z = df['x'].mean(), df['y'].mean(), df['z'].mean()
            features["com_x"] = float(com_x)
            features["com_y"] = float(com_y) 
            features["com_z"] = float(com_z)
            
            # Radio de giro
            r_squared = (df['x'] - com_x)**2 + (df['y'] - com_y)**2 + (df['z'] - com_z)**2
            features["gyration_radius"] = float(np.sqrt(r_squared.mean()))
            
            # Dispersión espacial
            features["spatial_std_x"] = float(df['x'].std())
            features["spatial_std_y"] = float(df['y'].std())
            features["spatial_std_z"] = float(df['z'].std())
            
            # Anisotropía espacial
            std_values = [df[col].std() for col in ['x', 'y', 'z']]
            max_std, min_std = max(std_values), min(std_values)
            features["spatial_anisotropy"] = float(max_std / min_std) if min_std > 0 else 1.0
            
            # Volumen envolvente
            x_range = df['x'].max() - df['x'].min()
            y_range = df['y'].max() - df['y'].min()
            z_range = df['z'].max() - df['z'].min()
            features["bounding_volume"] = float(x_range * y_range * z_range)
            
            # Compacidad
            if features["bounding_volume"] > 0:
                features["spatial_compactness"] = float(len(df) / features["bounding_volume"])
            else:
                features["spatial_compactness"] = 0.0
                
        except Exception as e:
            logger.warning(f"Error calculando features espaciales: {e}")
        
        return features
    
    def _extract_voronoi_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extraer features de volumen de Voronoi si están disponibles"""
        features = {}
        
        voro_cols = ["c_voro[1]", "voro_vol", "voronoi_volume"]
        voro_col = None
        for col in voro_cols:
            if col in df.columns:
                voro_col = col
                break
        
        if voro_col is None:
            return features
        
        try:
            voro_series = df[voro_col].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
            
            if len(voro_series) > 0:
                features["voro_vol_mean"] = float(voro_series.mean())
                features["voro_vol_std"] = float(voro_series.std())
                features["voro_vol_median"] = float(voro_series.median())
                features["voro_vol_min"] = float(voro_series.min())
                features["voro_vol_max"] = float(voro_series.max())
                
                if voro_series.mean() != 0:
                    features["voro_vol_cv"] = float(voro_series.std() / voro_series.mean())
                else:
                    features["voro_vol_cv"] = 0.0
                    
        except Exception as e:
            logger.warning(f"Error calculando features de Voronoi: {e}")
        
        return features
    
    def _extract_system_features(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> Dict[str, float]:
        """Extraer features del sistema filtrado"""
        features = {}
        
        # Número de átomos en región filtrada
        features["n_atoms_filtered"] = float(len(df))
        
        # Ratio de filtrado
        features["filter_ratio"] = float(metadata['_filter_ratio'])
        
        # Densidad efectiva en región filtrada
        if 'bounding_volume' in features and features['bounding_volume'] > 0:
            features["effective_density_filtered"] = float(len(df) / features['bounding_volume'])
        
        return features
    
    def _compute_file_hash(self, df: pd.DataFrame) -> str:
        """Calcular hash para tracking del archivo"""
        sample = df.head(20).to_string()
        return hashlib.md5(sample.encode()).hexdigest()[:8]
    
    def process_directory(self, dump_directory: str, 
                         output_csv_path: Optional[str] = None,
                         apply_stress: bool = False) -> pd.DataFrame:
        """
        Procesar directorio completo de archivos .dump
        
        Args:
            dump_directory: Directorio con archivos .dump
            output_csv_path: Ruta del archivo CSV de salida
            apply_stress: Si aplicar deformación afín
            
        Returns:
            DataFrame con todas las features extraídas
        """
        dump_dir = Path(dump_directory)
        
        # Buscar archivos .dump
        dump_files = list(dump_dir.glob("*.dump")) + list(dump_dir.glob("*.dump.gz"))
        
        if not dump_files:
            raise ValueError(f"No se encontraron archivos .dump en {dump_directory}")
        
        logger.info(f"Procesando {len(dump_files)} archivos .dump")
        
        # Procesar cada archivo
        all_features = []
        errors = []
        
        for i, dump_file in enumerate(sorted(dump_files)):
            try:
                logger.info(f"Procesando {i+1}/{len(dump_files)}: {dump_file.name}")
                
                features = self.process_dump_file(str(dump_file), apply_stress=apply_stress)
                features['_file_name'] = dump_file.name
                all_features.append(features)
                
            except Exception as e:
                error_msg = f"Error procesando {dump_file.name}: {str(e)}"
                logger.error(error_msg)
                errors.append({"file": str(dump_file), "error": str(e)})
        
        if not all_features:
            raise RuntimeError("No se pudieron procesar archivos válidos")
        
        # Crear DataFrame
        df_results = pd.DataFrame(all_features)
        
        # Guardar CSV
        if output_csv_path is None:
            output_csv_path = self.output_dir_csv / "unified_training_data.csv"
        
        df_results.to_csv(output_csv_path, index=False)
        logger.info(f"Resultados guardados en: {output_csv_path}")
        
        # Reporte final
        logger.info("=" * 50)
        logger.info("REPORTE FINAL")
        logger.info("=" * 50)
        logger.info(f"Archivos procesados exitosamente: {len(all_features)}")
        logger.info(f"Errores encontrados: {len(errors)}")
        
        if len(df_results) > 0:
            # Estadísticas de vacancies
            vac_stats = df_results['vacancies'].describe()
            logger.info(f"Rango de vacancies: {vac_stats['min']:.0f} - {vac_stats['max']:.0f}")
            logger.info(f"Media de vacancies: {vac_stats['mean']:.2f}")
            
            # Features extraídas
            feature_cols = [col for col in df_results.columns 
                           if not col.startswith('_') and col not in ['vacancies', 'file_hash']]
            logger.info(f"Features extraídas: {len(feature_cols)}")
            
            # Ratio de filtrado promedio
            if '_filter_ratio' in df_results.columns:
                avg_filter_ratio = df_results['_filter_ratio'].mean()
                logger.info(f"Ratio promedio de filtrado: {avg_filter_ratio:.3f}")
        
        logger.info("=" * 50)
        
        return df_results


# Función auxiliar para uso sencillo
def process_dumps_unified(
    dump_directory: str,
    atm_total: int,
    radius: float,
    smoothing_level: int = 0,
    output_csv: Optional[str] = None,
    apply_stress: bool = False
) -> pd.DataFrame:
    """
    Función auxiliar para procesar dumps con configuración simple
    
    Args:
        dump_directory: Directorio con archivos .dump
        atm_total: Número total de átomos en cristal perfecto
        radius: Radio para ConstructSurfaceModifier
        smoothing_level: Nivel de suavizado
        output_csv: Ruta del CSV de salida (opcional)
        apply_stress: Si aplicar deformación afín
        
    Returns:
        DataFrame con features y vacancies
    """
    processor = UnifiedTrainingProcessor(
        atm_total=atm_total,
        radius=radius,
        smoothing_level=smoothing_level
    )
    
    return processor.process_directory(
        dump_directory=dump_directory,
        output_csv_path=output_csv,
        apply_stress=apply_stress
    )