"""
Configuración centralizada para el procesador LAMMPS
"""

from dataclasses import dataclass
from enum import Enum
from typing import Set, Optional


class FeatureMode(Enum):
    """Modos de extracción de features con diferentes niveles de seguridad"""
    CONSERVATIVE = "conservative"  # Mínima fuga posible
    STANDARD = "standard"          # Balance entre información y fuga
    FULL = "full"                  # Todas las features (mayor riesgo)


@dataclass
class ProcessingConfig:
    """Configuración centralizada del procesador"""
    # Parámetros del sistema
    atm_total: int = 16384
    energy_min: float = -4.0
    energy_max: float = -3.0
    energy_bins: int = 10
    
    # Control de fuga de información
    feature_mode: FeatureMode = FeatureMode.STANDARD
    add_noise: bool = False
    noise_level: float = 0.01
    validate_features: bool = True
    
    # Features prohibidas para evitar fuga de información
    forbidden_features: Set[str] = None
    
    def __post_init__(self):
        if self.forbidden_features is None:
            self.forbidden_features = {
                'n_atoms', 'vacancy_fraction', 'vacancy_count',
                'atm_total_ref', 'direct_vacancy_count'
            }


class FeatureCategories:
    """Definición de categorías de features por riesgo de fuga"""
    
    HIGH_RISK = {
        'n_atoms', 'vacancy_fraction', 'vacancy_count',
        'coord_below_8', 'coord_perfect_12', 'coord_bin_4_5',
        'frac_coord_le_9', 'frac_coord_le_10', 'frac_coord_le_11'
    }
    
    MEDIUM_RISK = {
        'coord_bin_6_7', 'coord_bin_8_9', 'coord_bin_10_11',
        'frac_vm_top5', 'frac_pe_top5', 
        'coord2_le_3', 'coord2_le_4', 'coord2_le_5'
    }
    
    LOW_RISK = {
        'pe_mean', 'pe_std', 'pe_median',
        'stress_vm_mean', 'stress_vm_std',
        'stress_I1_mean', 'stress_I1_std',
        'coord_mean', 'coord_std', 'coord_entropy'
    }
    
    @classmethod
    def get_allowed_features(cls, mode: FeatureMode) -> Optional[Set[str]]:
        """Obtener conjunto de features permitidas según el modo"""
        if mode == FeatureMode.CONSERVATIVE:
            return cls.LOW_RISK
        elif mode == FeatureMode.STANDARD:
            return cls.LOW_RISK | cls.MEDIUM_RISK
        else:  # FULL
            return None  # Significa usar todas


# Constantes de validación
CORRELATION_THRESHOLD = 0.99  # Umbral para considerar fuga de información
MIN_ATOMS_THRESHOLD = 1000   # Mínimo número de átomos esperado
MAX_ATOMS_THRESHOLD = 20000  # Máximo número de átomos esperado