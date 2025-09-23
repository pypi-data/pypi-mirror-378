"""
Data processing module - CORREGIDO
Usa n_atoms fijo (16384) para features, n_atoms_real solo para target
"""

import pandas as pd
import numpy as np
import pickle
import json
import csv
import os
import gzip
import io
import math
from pathlib import Path
from typing import Union, List, Dict, Any, Optional, Tuple
import logging
from ..utils.validators import DataValidator
from ..utils.file_handlers import FileHandler

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Handles data loading, preprocessing, and feature selection
    CORREGIDO: Interfaz consistente con n_atoms fijo para features
    """
    
    def __init__(self):
        self.data = None
        self.original_data = None
        self.features = None
        self.target = None
        self.target_column = None
        self.file_handler = FileHandler()
        self.validator = DataValidator()
        
        # LAMMPS specific configuration
        self.ATM_TOTAL = 16384  # FIJO para features
        self.ENERGY_MIN = -4.0
        self.ENERGY_MAX = -3.0
        self.ENERGY_BINS = 10
        
        # Features prohibited for preventing data leakage
        self.FORBIDDEN_FEATURES = [
            'n_atoms', 'vacancy_fraction', 'vacancy_count', 'atm_total_ref'
        ]
    
    def load_data(self, file_path):
        """Load data from various file formats"""
        file_path = Path(file_path)
        if file_path.suffix == '.csv':
            self.current_data = pd.read_csv(file_path)
        elif file_path.suffix in ['.xlsx', '.xls']:
            self.current_data = pd.read_excel(file_path)
        elif file_path.suffix == '.json':
            self.current_data = pd.read_json(file_path)
        elif file_path.suffix == '.dump':
            self.current_data = self.load_dump_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        return self.current_data

    def load_dump_file(self, file_path):
        """Load .dump files (legacy method for pickle format)"""
        try:
            import pickle
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            raise ValueError(f"Error loading dump file: {str(e)}")
    
    def _is_lammps_dump_file(self, file_path: Path) -> bool:
        """Check if file is a LAMMPS dump file based on name patterns"""
        name = file_path.name.lower()
        patterns = ['dump.', '.dump', 'lammps', 'trj', 'traj']
        return any(pattern in name for pattern in patterns)
    
    def _detect_lammps_dump_content(self, file_path: Path) -> bool:
        """Detect LAMMPS dump format by examining file content"""
        try:
            opener = self._get_file_opener(file_path)
            with opener() as f:
                lines = []
                for i, line in enumerate(f):
                    lines.append(line.strip())
                    if i >= 10:
                        break
                
                lammps_headers = ['ITEM: TIMESTEP', 'ITEM: NUMBER OF ATOMS', 
                                'ITEM: BOX BOUNDS', 'ITEM: ATOMS']
                
                content = '\n'.join(lines)
                return any(header in content for header in lammps_headers)
        except Exception:
            return False
    
    def _get_file_opener(self, file_path: Path):
        """Get appropriate file opener based on extension"""
        if file_path.suffix.lower() == '.gz':
            return lambda: gzip.open(file_path, 'rt', encoding='utf-8')
        else:
            return lambda: open(file_path, 'r', encoding='utf-8')
    
    def _load_lammps_dump_file(self, file_path: Path) -> pd.DataFrame:
        """Load LAMMPS dump file and extract features"""
        try:
            df_atoms, n_atoms = self._parse_last_frame_dump(file_path)
            features = self._extract_features_from_atoms(df_atoms, n_atoms)
            features['filename'] = file_path.name
            result_df = pd.DataFrame([features])
            
            logger.info(f"Processed LAMMPS dump: {n_atoms} atoms, extracted {len(features)} features")
            return result_df

        except Exception as e:
            logger.error(f"Error processing LAMMPS dump file: {str(e)}")
            raise
    
    # Resto de métodos del DataProcessor original
    def export_to_csv(self, output_path: Union[str, Path]) -> None:
        """Export current data to CSV format"""
        if self.data is None:
            raise ValueError("No data loaded to export")
            
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.data.to_csv(output_path, index=False)
        logger.info(f"Data exported to: {output_path}")
    
    def get_column_info(self) -> Dict[str, Dict]:
        """Get detailed information about columns"""
        if self.data is None:
            return {}
            
        info = {}
        for col in self.data.columns:
            info[col] = {
                'dtype': str(self.data[col].dtype),
                'null_count': self.data[col].isnull().sum(),
                'unique_count': self.data[col].nunique(),
                'sample_values': self.data[col].dropna().head(5).tolist()
            }
            
            if self.data[col].dtype in ['int64', 'float64']:
                info[col].update({
                    'min': self.data[col].min(),
                    'max': self.data[col].max(),
                    'mean': self.data[col].mean(),
                    'std': self.data[col].std()
                })
                
        return info
    
    def select_features(self, feature_columns: List[str]) -> None:
        """Select feature columns for training"""
        if self.data is None:
            raise ValueError("No data loaded")
            
        missing_cols = [col for col in feature_columns if col not in self.data.columns]
        if missing_cols:
            raise ValueError(f"Columns not found: {missing_cols}")
            
        self.features = self.data[feature_columns].copy()
        logger.info(f"Selected {len(feature_columns)} features")
    
    def set_target(self, target_column: str) -> None:
        """Set target column for prediction"""
        if self.data is None:
            raise ValueError("No data loaded")
            
        if target_column not in self.data.columns:
            raise ValueError(f"Target column '{target_column}' not found")
            
        self.target = self.data[target_column].copy()
        self.target_column = target_column
        logger.info(f"Set target column: {target_column}")
    
    def get_training_data(self) -> tuple:
        """Get features and target for training"""
        if self.features is None or self.target is None:
            raise ValueError("Features and target must be selected first")
            
        return self.features, self.target
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the data"""
        if self.data is None:
            return {}
            
        return {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'memory_usage': self.data.memory_usage(deep=True).sum(),
            'numeric_columns': list(self.data.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(self.data.select_dtypes(include=['object']).columns),
            'lammps_features': self._get_lammps_feature_summary() if self._has_lammps_features() else None
        }
    
    def _has_lammps_features(self) -> bool:
        """Check if the dataset contains LAMMPS-derived features"""
        if self.data is None:
            return False
        
        lammps_indicators = ['coord_', 'pe_', 'stress_', 'voro_', 'vacancies']
        return any(any(indicator in col for col in self.data.columns) 
                  for indicator in lammps_indicators)
    
    def _get_lammps_feature_summary(self) -> Dict[str, Any]:
        """Get summary of LAMMPS-specific features"""
        if self.data is None:
            return {}
        
        feature_categories = {
            'coordination': [col for col in self.data.columns if 'coord' in col.lower()],
            'energy': [col for col in self.data.columns if 'pe_' in col or 'energy' in col.lower()],
            'stress': [col for col in self.data.columns if 'stress' in col.lower() or 'vm' in col.lower()],
            'voronoi': [col for col in self.data.columns if 'voro' in col.lower()],
            'bulk_indicators': [col for col in self.data.columns if 'frac_' in col.lower()],
            'histograms': [col for col in self.data.columns if '_bin_' in col.lower()]
        }
        
        summary = {}
        for category, features in feature_categories.items():
            if features:
                summary[category] = {
                    'count': len(features),
                    'features': features[:5],  # Show first 5 features
                    'has_more': len(features) > 5
                }
        
        # Add vacancy information if present
        if 'vacancies' in self.data.columns:
            vacancy_stats = self.data['vacancies'].describe()
            summary['vacancies'] = {
                'min': vacancy_stats['min'],
                'max': vacancy_stats['max'], 
                'mean': vacancy_stats['mean'],
                'std': vacancy_stats['std'],
                'unique_values': self.data['vacancies'].nunique()
            }
        
        return summary
            
    
    def _parse_last_frame_dump(self, file_path: Path) -> Tuple[pd.DataFrame, int]:
        """Parse the LAST frame from a LAMMPS dump file"""
        opener = self._get_file_opener(file_path)
        
        with opener() as f:
            lines = f.read().splitlines()
        
        atoms_headers = [i for i, line in enumerate(lines) if line.startswith("ITEM: ATOMS")]
        
        if not atoms_headers:
            raise RuntimeError(f"No 'ITEM: ATOMS' found in {file_path}")
        
        start_idx = atoms_headers[-1]
        header_line = lines[start_idx]
        header_parts = header_line.replace("ITEM: ATOMS", "").strip().split()
        
        # Find number of atoms
        n_atoms = None
        for j in range(start_idx - 1, -1, -1):
            if lines[j].startswith("ITEM: NUMBER OF ATOMS"):
                n_atoms = int(lines[j + 1].strip())
                break
        
        if n_atoms is None:
            raise RuntimeError(f"Could not find number of atoms for {file_path}")
        
        data_start = start_idx + 1
        data_end = data_start + n_atoms
        
        if data_end > len(lines):
            raise RuntimeError(f"Not enough data lines in {file_path}")
        
        atomic_data = []
        for line_idx in range(data_start, data_end):
            parts = lines[line_idx].split()
            row = []
            
            for i, part in enumerate(parts):
                if i < len(header_parts):
                    try:
                        row.append(float(part))
                    except ValueError:
                        row.append(np.nan)
                        
            atomic_data.append(row)
        
        df = pd.DataFrame(atomic_data, columns=header_parts[:len(atomic_data[0])])
        return df, n_atoms
    
    def _extract_features_from_atoms(self, df: pd.DataFrame, n_atoms_real: int) -> Dict[str, Any]:
        """
        Extract features from atomic DataFrame for ML
        CORREGIDO: Usa self.ATM_TOTAL fijo internamente
        
        Args:
            df: DataFrame with atomic data
            n_atoms_real: Real number of atoms (used only for target calculation)
            
        Returns:
            Dictionary with extracted features
        """
        # Add stress invariants if stress data is available
        df = self._add_stress_invariants(df)
        
        # Get atomic properties
        properties = self._get_atomic_properties(df)
        
        features = {}
        
        # Calculate aggregated statistics for each property
        for prop_name, prop_series in properties.items():
            features.update(self._calculate_aggregated_stats(prop_series, prop_name))
        
        # Add bulk defect indicators (usando ATM_TOTAL fijo internamente)
        features.update(self._calculate_bulk_indicators(properties))
        
        # Add coordination histogram (usando ATM_TOTAL fijo internamente)
        if 'coord' in properties:
            coord_hist = self._compute_coordination_histogram(properties['coord'])
            features.update(coord_hist)
        
        # Add energy histogram (usando ATM_TOTAL fijo internamente)
        if 'pe' in properties:
            energy_hist = self._compute_energy_histogram(properties['pe'])
            features.update(energy_hist)
        
        # TARGET: Calcular vacancies con n_atoms_real (no es feature)
        vacancies = int(self.ATM_TOTAL - n_atoms_real)
        features['vacancies'] = vacancies
        
        # Metadata (no son features de ML)
        features["_n_atoms_real"] = n_atoms_real
        features["_n_atoms_fixed_for_features"] = self.ATM_TOTAL
        
        # Remove forbidden features that could cause data leakage
        for forbidden in self.FORBIDDEN_FEATURES:
            features.pop(forbidden, None)
        
        return features
    
    def _calculate_bulk_indicators(self, properties: Dict[str, pd.Series]) -> Dict[str, float]:
        """Calculate bulk defect indicators - CORREGIDO: usa self.ATM_TOTAL internamente"""
        indicators = {}
        
        # Coordination-based indicators (estas son fracciones, no dependen del total)
        if 'coord' in properties:
            coord = properties['coord'].dropna()
            if len(coord) > 0:
                indicators['frac_coord_le_11'] = float((coord <= 11).mean())
                indicators['frac_coord_le_10'] = float((coord <= 10).mean())
                indicators['frac_coord_le_9'] = float((coord <= 9).mean())
        
        # Second shell coordination indicators
        if 'coord2' in properties:
            coord2 = properties['coord2'].dropna()
            if len(coord2) > 0:
                indicators['frac_coord2_le_5'] = float((coord2 <= 5).mean())
                indicators['frac_coord2_le_4'] = float((coord2 <= 4).mean())
                indicators['frac_coord2_le_3'] = float((coord2 <= 3).mean())
        
        # High stress indicators (fracciones, no dependen del total)
        if 'stress_vm' in properties:
            stress_vm = properties['stress_vm'].dropna()
            if len(stress_vm) > 0:
                threshold = stress_vm.quantile(0.95)
                indicators['frac_vm_top5'] = float((stress_vm >= threshold).mean())
        
        # High energy indicators (fracciones, no dependen del total)
        if 'pe' in properties:
            pe = properties['pe'].dropna()
            if len(pe) > 0:
                threshold = pe.quantile(0.95)
                indicators['frac_pe_top5'] = float((pe >= threshold).mean())
        
        # NUEVO: Density features usando self.ATM_TOTAL
        if 'voro_vol' in properties:
            voro_vol = properties['voro_vol'].dropna()
            if len(voro_vol) > 0:
                avg_voro_vol = voro_vol.mean()
                if avg_voro_vol > 0:
                    indicators['atomic_density_fixed'] = float(self.ATM_TOTAL / (avg_voro_vol * len(voro_vol)))
                else:
                    indicators['atomic_density_fixed'] = 0.0
        
        return indicators
    
    def _compute_coordination_histogram(self, coord_series: pd.Series) -> Dict[str, float]:
        """Compute coordination histogram - CORREGIDO: usa self.ATM_TOTAL internamente"""
        coord_clean = coord_series.replace([np.inf, -np.inf], np.nan).dropna()
        
        hist_features = {}
        
        if len(coord_clean) == 0:
            # Default values if no data
            bins = ['4_5', '6_7', '8_9', '10_11', '12']
            for bin_name in bins:
                hist_features[f"coord_bin_{bin_name}"] = 0.0
            hist_features["coord_below_8"] = 0.0
            hist_features["coord_perfect_12"] = 0.0
            return hist_features
        
        # CORREGIDO: Usar self.ATM_TOTAL fijo
        total_fixed = self.ATM_TOTAL
        
        # Bin counts - normalizados por ATM_TOTAL
        hist_features["coord_bin_4_5"] = float(((coord_clean >= 4) & (coord_clean <= 5)).sum() / total_fixed)
        hist_features["coord_bin_6_7"] = float(((coord_clean >= 6) & (coord_clean <= 7)).sum() / total_fixed)
        hist_features["coord_bin_8_9"] = float(((coord_clean >= 8) & (coord_clean <= 9)).sum() / total_fixed)
        hist_features["coord_bin_10_11"] = float(((coord_clean >= 10) & (coord_clean <= 11)).sum() / total_fixed)
        hist_features["coord_bin_12"] = float((coord_clean >= 12).sum() / total_fixed)
        
        # Special indicators - normalizados por ATM_TOTAL
        hist_features["coord_below_8"] = float((coord_clean < 8).sum() / total_fixed)
        hist_features["coord_perfect_12"] = float((coord_clean == 12).sum() / total_fixed)
        
        return hist_features
    
    def _compute_energy_histogram(self, pe_series: pd.Series) -> Dict[str, float]:
        """Compute energy histogram - CORREGIDO: usa self.ATM_TOTAL internamente"""
        pe_clean = pe_series.replace([np.inf, -np.inf], np.nan).dropna()
        
        hist_features = {}
        
        if len(pe_clean) == 0:
            # Default values if no data
            for i in range(self.ENERGY_BINS):
                hist_features[f"pe_bin_{i}"] = 0.0
            hist_features["pe_below_min"] = 0.0
            hist_features["pe_above_max"] = 0.0
            return hist_features
        
        # CORREGIDO: Usar self.ATM_TOTAL para normalización
        total_fixed = self.ATM_TOTAL
        
        # Create histogram bins
        bin_edges = np.linspace(self.ENERGY_MIN, self.ENERGY_MAX, self.ENERGY_BINS + 1)
        hist, _ = np.histogram(pe_clean, bins=bin_edges)
        
        # Bin features - normalizados por ATM_TOTAL
        for i in range(self.ENERGY_BINS):
            hist_features[f"pe_bin_{i}"] = float(hist[i] / total_fixed)
        
        # Out-of-range features - normalizados por ATM_TOTAL  
        hist_features["pe_below_min"] = float((pe_clean < self.ENERGY_MIN).sum() / total_fixed)
        hist_features["pe_above_max"] = float((pe_clean > self.ENERGY_MAX).sum() / total_fixed)
        
        # Absolute minimum energy (no depende del número de átomos)
        hist_features["pe_absolute_min"] = float(pe_clean.min())
        
        return hist_features
    
    def _add_stress_invariants(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add stress invariants (I1 and von Mises) if stress components are available"""
        stress_cols = [f"c_satom[{i}]" for i in range(1, 7)]
        
        if not all(col in df.columns for col in stress_cols):
            return df
        
        df = df.copy()
        
        # Extract stress components
        sxx, syy, szz, sxy, sxz, syz = [df[col].astype(float) for col in stress_cols]
        
        # Calculate invariants
        I1 = sxx + syy + szz  # First invariant (trace)
        mean_normal = I1 / 3.0
        
        # Deviatoric stress components
        sxx_dev = sxx - mean_normal
        syy_dev = syy - mean_normal
        szz_dev = szz - mean_normal
        
        # von Mises stress
        von_mises = np.sqrt(1.5 * (sxx_dev**2 + syy_dev**2 + szz_dev**2 + 
                                  2 * (sxy**2 + sxz**2 + syz**2)))
        
        df["stress_I1"] = I1
        df["stress_vm"] = von_mises
        
        return df
    
    def _get_atomic_properties(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Extract atomic properties from DataFrame"""
        properties = {}
        
        # Potential energy
        pe_candidates = ["c_peatom", "pe", "c_pe", "v_pe"]
        for candidate in pe_candidates:
            if candidate in df.columns:
                properties["pe"] = df[candidate].astype(float)
                break
        
        # Stress invariants (if calculated)
        if "stress_I1" in df.columns:
            properties["stress_I1"] = df["stress_I1"].astype(float)
        if "stress_vm" in df.columns:
            properties["stress_vm"] = df["stress_vm"].astype(float)
        
        # Individual stress components
        stress_components = {
            1: "sxx", 2: "syy", 3: "szz", 
            4: "sxy", 5: "sxz", 6: "syz"
        }
        for i, name in stress_components.items():
            col = f"c_satom[{i}]"
            if col in df.columns:
                properties[name] = df[col].astype(float)
        
        # Coordination numbers
        coord_candidates = ["c_coord", "coord", "c_coord1"]
        for candidate in coord_candidates:
            if candidate in df.columns:
                properties["coord"] = df[candidate].astype(float)
                break
        
        # Second shell coordination
        coord2_candidates = ["c_coord2", "coord2", "c_coord_2nd"]
        for candidate in coord2_candidates:
            if candidate in df.columns:
                properties["coord2"] = df[candidate].astype(float)
                break
        
        # Voronoi volume
        if "c_voro[1]" in df.columns:
            properties["voro_vol"] = df["c_voro[1]"].astype(float)
        
        # Kinetic energy
        ke_candidates = ["c_keatom", "ke"]
        for candidate in ke_candidates:
            if candidate in df.columns:
                properties["ke"] = df[candidate].astype(float)
                break
        
        return properties
    
    def _calculate_aggregated_stats(self, series: pd.Series, prefix: str) -> Dict[str, float]:
        """Calculate aggregated statistics for a property series"""
        clean_series = pd.to_numeric(series, errors='coerce').replace([np.inf, -np.inf], np.nan).dropna()
        
        if clean_series.empty:
            stats_keys = ['min', 'p10', 'p25', 'median', 'p75', 'p90', 'max', 'mean', 'std', 'skew', 'kurt']
            return {f"{prefix}_{key}": np.nan for key in stats_keys}
        
        # Calculate quantiles
        quantiles = clean_series.quantile([0.10, 0.25, 0.50, 0.75, 0.90])
        
        stats = {
            f"{prefix}_min": float(clean_series.min()),
            f"{prefix}_p10": float(quantiles.loc[0.10]),
            f"{prefix}_p25": float(quantiles.loc[0.25]),
            f"{prefix}_median": float(quantiles.loc[0.50]),
            f"{prefix}_p75": float(quantiles.loc[0.75]),
            f"{prefix}_p90": float(quantiles.loc[0.90]),
            f"{prefix}_max": float(clean_series.max()),
            f"{prefix}_mean": float(clean_series.mean()),
            f"{prefix}_std": float(clean_series.std(ddof=1)) if len(clean_series) > 1 else 0.0,
            f"{prefix}_skew": float(clean_series.skew()) if len(clean_series) > 2 else 0.0,
            f"{prefix}_kurt": float(clean_series.kurtosis()) if len(clean_series) > 3 else 0.0,
        }
        
        return stats
    
    # Resto de métodos (process_lammps_batch, etc.) permanecen igual
    def process_lammps_batch(self, directory_path: Union[str, Path], 
                            file_patterns: List[str] = None,
                            recursive: bool = True,
                            atm_total: int = None) -> pd.DataFrame:
        """Process multiple LAMMPS dump files from a directory"""
        if atm_total is not None:
            self.ATM_TOTAL = atm_total
            
        if file_patterns is None:
            file_patterns = ["*.dump", "*.dump.gz", "dump.*", "*.lammps", "*.trj"]
        
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        dump_files = []
        for pattern in file_patterns:
            if recursive:
                dump_files.extend(directory.rglob(pattern))
            else:
                dump_files.extend(directory.glob(pattern))
        
        dump_files = sorted(list(set(dump_files)))
        
        if not dump_files:
            raise ValueError(f"No dump files found in {directory_path}")
        
        logger.info(f"Found {len(dump_files)} dump files to process")
        
        processed_data = []
        failed_files = []
        
        for i, file_path in enumerate(dump_files, 1):
            try:
                logger.info(f"Processing {i}/{len(dump_files)}: {file_path.name}")
                
                df_atoms, n_atoms = self._parse_last_frame_dump(file_path)
                features = self._extract_features_from_atoms(df_atoms, n_atoms)
                features['filename'] = file_path.name
                
                processed_data.append(features)
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {str(e)}")
                failed_files.append(str(file_path))
        
        if not processed_data:
            raise ValueError("No files were processed successfully")
        
        result_df = pd.DataFrame(processed_data)
        result_df.set_index('filename', inplace=True)
        
        logger.info(f"Successfully processed {len(processed_data)} files")
        if failed_files:
            logger.warning(f"Failed to process {len(failed_files)} files: {failed_files}")
        
        logger.info(f"Generated dataset with {len(result_df)} rows and {len(result_df.columns)} columns")
        
        self.data = result_df
        self.original_data = result_df.copy()
        
        return result_df