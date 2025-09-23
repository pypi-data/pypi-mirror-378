"""
Data processing module - MODIFICADO para usar n_atoms fijo en features
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
    MODIFICADO: Usa ATM_TOTAL fijo para cálculos de features
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
        self.ATM_TOTAL = 16384
        self.ENERGY_MIN = -4.0
        self.ENERGY_MAX = -3.0
        self.ENERGY_BINS = 10
        
        # Features prohibited for preventing data leakage
        self.FORBIDDEN_FEATURES = [
            'n_atoms', 'vacancy_fraction', 'vacancy_count', 'atm_total_ref'
        ]
    
    # ... (métodos de carga sin cambios) ...
    
    def _extract_features_from_atoms(self, df: pd.DataFrame, n_atoms_real: int) -> Dict[str, Any]:
        """
        Extract features from atomic DataFrame for ML
        MODIFICADO: Usa ATM_TOTAL fijo para features, n_atoms_real solo para target
        
        Args:
            df: DataFrame with atomic data
            n_atoms_real: Real number of atoms in the system (solo para target)
            
        Returns:
            Dictionary with extracted features
        """
        # Add stress invariants if stress data is available
        df = self._add_stress_invariants(df)
        
        # Get atomic properties
        properties = self._get_atomic_properties(df)
        
        features = {}
        
        # CRÍTICO: Usar ATM_TOTAL fijo para todos los cálculos de features
        n_atoms_fixed = self.ATM_TOTAL
        
        # Calculate aggregated statistics for each property
        for prop_name, prop_series in properties.items():
            features.update(self._calculate_aggregated_stats(prop_series, prop_name))
        
        # Add bulk defect indicators (usa ATM_TOTAL fijo)
        features.update(self._calculate_bulk_indicators(properties, n_atoms_fixed))
        
        # Add coordination histogram (usa ATM_TOTAL fijo)
        if 'coord' in properties:
            coord_hist = self._compute_coordination_histogram(properties['coord'], n_atoms_fixed)
            features.update(coord_hist)
        
        # Add energy histogram (usa ATM_TOTAL fijo)
        if 'pe' in properties:
            energy_hist = self._compute_energy_histogram(properties['pe'], n_atoms_fixed)
            features.update(energy_hist)
        
        # TARGET: Calcular vacancies con n_atoms_real (no es feature)
        vacancies = int(self.ATM_TOTAL - n_atoms_real)
        features['vacancies'] = vacancies
        
        # Metadata (no son features de ML)
        features["_n_atoms_real"] = n_atoms_real
        features["_n_atoms_fixed_for_features"] = n_atoms_fixed
        
        # Remove forbidden features that could cause data leakage
        for forbidden in self.FORBIDDEN_FEATURES:
            features.pop(forbidden, None)
        
        return features
    
    def _calculate_bulk_indicators(self, properties: Dict[str, pd.Series], n_atoms_fixed: int) -> Dict[str, float]:
        """Calculate bulk defect indicators usando n_atoms_fixed"""
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
        
        # NUEVO: Density features usando n_atoms_fixed
        if 'voro_vol' in properties:
            voro_vol = properties['voro_vol'].dropna()
            if len(voro_vol) > 0:
                # Densidad basada en volumen de Voronoi usando n_atoms_fixed
                avg_voro_vol = voro_vol.mean()
                indicators['atomic_density_fixed'] = float(n_atoms_fixed / (avg_voro_vol * len(voro_vol))) if avg_voro_vol > 0 else 0.0
        
        return indicators
    
    def _compute_coordination_histogram(self, coord_series: pd.Series, n_atoms_fixed: int) -> Dict[str, float]:
        """Compute coordination number histogram usando n_atoms_fixed"""
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
        
        # MODIFICADO: Usar n_atoms_fixed en lugar de len(coord_clean)
        total_fixed = n_atoms_fixed
        
        # Bin counts - normalizados por n_atoms_fixed
        hist_features["coord_bin_4_5"] = float(((coord_clean >= 4) & (coord_clean <= 5)).sum() / total_fixed)
        hist_features["coord_bin_6_7"] = float(((coord_clean >= 6) & (coord_clean <= 7)).sum() / total_fixed)
        hist_features["coord_bin_8_9"] = float(((coord_clean >= 8) & (coord_clean <= 9)).sum() / total_fixed)
        hist_features["coord_bin_10_11"] = float(((coord_clean >= 10) & (coord_clean <= 11)).sum() / total_fixed)
        hist_features["coord_bin_12"] = float((coord_clean >= 12).sum() / total_fixed)
        
        # Special indicators - normalizados por n_atoms_fixed
        hist_features["coord_below_8"] = float((coord_clean < 8).sum() / total_fixed)
        hist_features["coord_perfect_12"] = float((coord_clean == 12).sum() / total_fixed)
        
        return hist_features
    
    def _compute_energy_histogram(self, pe_series: pd.Series, n_atoms_fixed: int) -> Dict[str, float]:
        """Compute potential energy histogram usando n_atoms_fixed"""
        pe_clean = pe_series.replace([np.inf, -np.inf], np.nan).dropna()
        
        hist_features = {}
        
        if len(pe_clean) == 0:
            # Default values if no data
            for i in range(self.ENERGY_BINS):
                hist_features[f"pe_bin_{i}"] = 0.0
            hist_features["pe_below_min"] = 0.0
            hist_features["pe_above_max"] = 0.0
            return hist_features
        
        # MODIFICADO: Usar n_atoms_fixed para normalización
        total_fixed = n_atoms_fixed
        
        # Create histogram bins
        bin_edges = np.linspace(self.ENERGY_MIN, self.ENERGY_MAX, self.ENERGY_BINS + 1)
        hist, _ = np.histogram(pe_clean, bins=bin_edges)
        
        # Bin features - normalizados por n_atoms_fixed
        for i in range(self.ENERGY_BINS):
            hist_features[f"pe_bin_{i}"] = float(hist[i] / total_fixed)
        
        # Out-of-range features - normalizados por n_atoms_fixed
        hist_features["pe_below_min"] = float((pe_clean < self.ENERGY_MIN).sum() / total_fixed)
        hist_features["pe_above_max"] = float((pe_clean > self.ENERGY_MAX).sum() / total_fixed)
        
        # Absolute minimum energy (este no depende del número de átomos)
        hist_features["pe_absolute_min"] = float(pe_clean.min())
        
        return hist_features
    
    def process_lammps_batch(self, directory_path: Union[str, Path], 
                            file_patterns: List[str] = None,
                            recursive: bool = True,
                            atm_total: int = None) -> pd.DataFrame:
        """
        Process multiple LAMMPS dump files from a directory
        
        Args:
            directory_path: Directory containing dump files
            file_patterns: Patterns to match filenames (default: common LAMMPS patterns)
            recursive: Whether to search recursively
            atm_total: Total number of atoms (for vacancy calculation)
            
        Returns:
            DataFrame with features from all processed files
        """
        if atm_total is not None:
            self.ATM_TOTAL = atm_total
            
        if file_patterns is None:
            file_patterns = ["*.dump", "*.dump.gz", "dump.*", "*.lammps", "*.trj"]
        
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find all dump files
        dump_files = []
        for pattern in file_patterns:
            if recursive:
                dump_files.extend(directory.rglob(pattern))
            else:
                dump_files.extend(directory.glob(pattern))
        
        # Remove duplicates and sort
        dump_files = sorted(list(set(dump_files)))
        
        if not dump_files:
            raise ValueError(f"No dump files found in {directory_path}")
        
        logger.info(f"Found {len(dump_files)} dump files to process")
        
        # Process each file
        processed_data = []
        failed_files = []
        
        for i, file_path in enumerate(dump_files, 1):
            try:
                logger.info(f"Processing {i}/{len(dump_files)}: {file_path.name}")
                
                # Parse dump file
                df_atoms, n_atoms = self._parse_last_frame_dump(file_path)
                
                # Extract features
                features = self._extract_features_from_atoms(df_atoms, n_atoms)
                features['filename'] = file_path.name
                
                processed_data.append(features)
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {str(e)}")
                failed_files.append(str(file_path))
        
        if not processed_data:
            raise ValueError("No files were processed successfully")
        
        # Create final DataFrame
        result_df = pd.DataFrame(processed_data)
        result_df.set_index('filename', inplace=True)
        
        # Log summary
        logger.info(f"Successfully processed {len(processed_data)} files")
        if failed_files:
            logger.warning(f"Failed to process {len(failed_files)} files: {failed_files}")
        
        logger.info(f"Generated dataset with {len(result_df)} rows and {len(result_df.columns)} columns")
        
        self.data = result_df
        self.original_data = result_df.copy()
        
        return result_df
    
    # Keep all existing methods from original DataProcessor...
    def _load_dump_file(self, file_path: Path) -> pd.DataFrame:
        """
        Load data from .dump files (legacy method for pickle format)
        """
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                
            # Handle different dump formats
            if isinstance(data, pd.DataFrame):
                return data
            elif isinstance(data, dict):
                return pd.DataFrame(data)
            elif isinstance(data, list):
                # Try to convert list to DataFrame
                if len(data) > 0 and isinstance(data[0], dict):
                    return pd.DataFrame(data)
                else:
                    # Create DataFrame with single column
                    return pd.DataFrame({'data': data})
            else:
                # Try to convert to DataFrame
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error loading dump file: {str(e)}")
            # Try alternative approaches
            try:
                # Try reading as text and parsing
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Try JSON parsing
                    data = json.loads(content)
                    return pd.DataFrame(data)
            except:
                raise ValueError(f"Unable to parse dump file: {file_path}")
    
    def _load_json_file(self, file_path: Path) -> pd.DataFrame:
        """Load JSON or JSONL files"""
        if file_path.suffix.lower() == '.jsonl':
            # Handle JSON Lines format
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    data.append(json.loads(line.strip()))
            return pd.DataFrame(data)
        else:
            # Handle regular JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return pd.DataFrame(data)
    
    # ... (rest of existing methods remain unchanged)
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
    
    def preprocess_data(self, 
                       handle_missing: str = 'drop',
                       encode_categorical: bool = True,
                       scale_numeric: bool = False) -> None:
        """Preprocess the data"""
        if self.features is None or self.target is None:
            raise ValueError("Features and target must be selected first")
        
        # Handle missing values
        if handle_missing == 'drop':
            # Drop rows with any missing values
            mask = ~(self.features.isnull().any(axis=1) | self.target.isnull())
            self.features = self.features[mask]
            self.target = self.target[mask]
        elif handle_missing == 'fill_mean':
            self.features = self.features.fillna(self.features.mean())
        elif handle_missing == 'fill_median':
            self.features = self.features.fillna(self.features.median())
        elif handle_missing == 'fill_mode':
            self.features = self.features.fillna(self.features.mode().iloc[0])
            
        # Encode categorical variables
        if encode_categorical:
            categorical_columns = self.features.select_dtypes(include=['object']).columns
            for col in categorical_columns:
                self.features[col] = pd.Categorical(self.features[col]).codes
                
        # Scale numeric variables
        if scale_numeric:
            from sklearn.preprocessing import StandardScaler
            numeric_columns = self.features.select_dtypes(include=[np.number]).columns
            scaler = StandardScaler()
            self.features[numeric_columns] = scaler.fit_transform(self.features[numeric_columns])
            
        logger.info("Data preprocessing completed")
    
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
    
    def set_lammps_config(self, atm_total: int = None, energy_min: float = None, 
                         energy_max: float = None, energy_bins: int = None) -> None:
        """
        Update LAMMPS processing configuration
        
        Args:
            atm_total: Total number of atoms in perfect crystal
            energy_min: Minimum energy for histogram
            energy_max: Maximum energy for histogram  
            energy_bins: Number of energy bins
        """
        if atm_total is not None:
            self.ATM_TOTAL = atm_total
        if energy_min is not None:
            self.ENERGY_MIN = energy_min
        if energy_max is not None:
            self.ENERGY_MAX = energy_max
        if energy_bins is not None:
            self.ENERGY_BINS = energy_bins
            
        logger.info(f"Updated LAMMPS config: atoms={self.ATM_TOTAL}, "
                   f"energy=[{self.ENERGY_MIN}, {self.ENERGY_MAX}], bins={self.ENERGY_BINS}")
    
    def validate_lammps_dataset(self) -> Dict[str, Any]:
        """
        Validate a LAMMPS-derived dataset for common issues
        
        Returns:
            Dict with validation results and recommendations
        """
        if self.data is None:
            return {"error": "No data loaded"}
        
        validation = {
            "is_lammps_dataset": self._has_lammps_features(),
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "data_quality": {}
        }
        
        if not validation["is_lammps_dataset"]:
            validation["warnings"].append("Dataset doesn't appear to contain LAMMPS features")
            return validation
        
        # Check for data leakage features
        forbidden_present = [col for col in self.FORBIDDEN_FEATURES if col in self.data.columns]
        if forbidden_present:
            validation["issues"].append(f"Found forbidden features that may cause data leakage: {forbidden_present}")
            validation["recommendations"].append("Remove forbidden features before training")
        
        # Check vacancy distribution
        if 'vacancies' in self.data.columns:
            vacancy_stats = self.data['vacancies'].describe()
            validation["data_quality"]["vacancy_range"] = (vacancy_stats['min'], vacancy_stats['max'])
            
            if vacancy_stats['std'] == 0:
                validation["warnings"].append("All samples have the same number of vacancies")
            
            if vacancy_stats['min'] < 0:
                validation["issues"].append("Found negative vacancy counts")
        
        # Check for missing values in key features
        key_features = [col for col in self.data.columns if any(key in col.lower() 
                       for key in ['coord', 'pe_', 'stress', 'vacancies'])]
        
        missing_in_key = {col: self.data[col].isnull().sum() for col in key_features 
                         if self.data[col].isnull().sum() > 0}
        
        if missing_in_key:
            validation["warnings"].append(f"Missing values in key features: {missing_in_key}")
            validation["recommendations"].append("Consider imputation or removal of samples with missing key features")
        
        # Check for extreme outliers
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        outlier_features = []
        
        for col in numeric_cols:
            if col != 'vacancies':  # Skip target variable
                q1 = self.data[col].quantile(0.25)
                q3 = self.data[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 3 * iqr  # More strict than typical 1.5*IQR
                upper_bound = q3 + 3 * iqr
                
                outliers = ((self.data[col] < lower_bound) | (self.data[col] > upper_bound)).sum()
                if outliers > len(self.data) * 0.05:  # More than 5% outliers
                    outlier_features.append(f"{col} ({outliers} outliers)")
        
        if outlier_features:
            validation["warnings"].append(f"High number of outliers in: {outlier_features[:3]}")
            validation["recommendations"].append("Consider outlier detection and removal")
        
        # Data quality summary
        validation["data_quality"].update({
            "total_samples": len(self.data),
            "total_features": len(self.data.columns),
            "missing_percentage": (self.data.isnull().sum().sum() / (len(self.data) * len(self.data.columns))) * 100,
            "numeric_features": len(self.data.select_dtypes(include=[np.number]).columns),
            "categorical_features": len(self.data.select_dtypes(include=['object']).columns)
        })
        
        return validation