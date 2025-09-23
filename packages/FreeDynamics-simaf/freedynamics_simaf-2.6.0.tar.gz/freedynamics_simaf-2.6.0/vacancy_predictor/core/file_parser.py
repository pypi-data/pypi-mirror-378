"""
Parser de archivos LAMMPS dump - Responsabilidad única de parsing
"""

import pandas as pd
import numpy as np
import gzip
import io
from pathlib import Path
from typing import Tuple, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class LAMMPSFileParser:
    """Parser especializado para archivos LAMMPS dump"""
    
    def __init__(self):
        self.supported_extensions = ['.dump', '.dump.gz', '.lammpstrj', '.lammpstrj.gz']
    
    def _open_file(self, path: str):
        """Abrir archivo, detectando si está comprimido"""
        p = Path(path)
        if p.suffix == ".gz":
            return io.TextIOWrapper(gzip.open(p, "rb"), encoding="utf-8", newline="")
        return open(p, "r", encoding="utf-8", newline="")
    
    def parse_last_frame(self, path: str) -> Tuple[pd.DataFrame, int, Dict[str, Any]]:
        """
        Parser robusto del último frame de un archivo LAMMPS dump
        
        Returns:
            df: DataFrame con datos de átomos
            n_atoms: Número de átomos
            metadata: Información adicional del frame
        """
        try:
            with self._open_file(path) as f:
                lines = f.read().splitlines()
        except Exception as e:
            raise RuntimeError(f"Error leyendo archivo {path}: {str(e)}")
        
        # Buscar la última sección ATOMS
        atoms_indices = [i for i, line in enumerate(lines) 
                        if line.startswith("ITEM: ATOMS")]
        
        if not atoms_indices:
            raise RuntimeError(f"No se encontró 'ITEM: ATOMS' en {path}")
        
        start_idx = atoms_indices[-1]
        
        # Extraer metadata del frame
        metadata = self._extract_metadata(lines, start_idx)
        
        # Parsear header de átomos
        header_line = lines[start_idx].replace("ITEM: ATOMS", "").strip()
        columns = header_line.split()
        
        if not columns:
            raise RuntimeError(f"Header de ATOMS vacío en {path}")
        
        # Determinar número de átomos
        n_atoms = self._find_num_atoms(lines, start_idx, metadata)
        
        if n_atoms <= 0:
            raise RuntimeError(f"Número inválido de átomos ({n_atoms}) en {path}")
        
        # Parsear datos de átomos
        df = self._parse_atomic_data(lines, start_idx + 1, n_atoms, columns)
        
        # Validar que tenemos datos
        if df.empty:
            raise RuntimeError(f"No se pudieron extraer datos de átomos de {path}")
        
        logger.debug(f"Parseado {Path(path).name}: {len(df)} átomos, {len(df.columns)} columnas")
        
        return df, len(df), metadata
    
    def _extract_metadata(self, lines: List[str], atoms_start: int) -> Dict[str, Any]:
        """Extraer metadata del frame (timestep, box bounds, etc.)"""
        metadata = {}
        
        # Buscar hacia atrás desde ITEM: ATOMS
        search_range = range(max(0, atoms_start - 50), atoms_start)
        
        for i in search_range:
            line = lines[i].strip()
            
            if line.startswith("ITEM: TIMESTEP") and i + 1 < len(lines):
                try:
                    metadata['timestep'] = int(lines[i + 1].strip())
                except ValueError:
                    pass
            
            elif line.startswith("ITEM: BOX BOUNDS"):
                box_bounds = []
                for k in range(1, 4):  # Leer siguientes 3 líneas
                    if i + k < len(lines):
                        bounds_line = lines[i + k].split()
                        if len(bounds_line) >= 2:
                            try:
                                box_bounds.append([float(bounds_line[0]), float(bounds_line[1])])
                            except ValueError:
                                pass
                
                if len(box_bounds) == 3:
                    metadata['box_bounds'] = box_bounds
                    # Calcular volumen
                    dimensions = [b[1] - b[0] for b in box_bounds]
                    metadata['box_volume'] = np.prod(dimensions)
        
        return metadata
    
    def _find_num_atoms(self, lines: List[str], atoms_start: int, metadata: Dict) -> int:
        """Determinar número de átomos del frame"""
        # Buscar ITEM: NUMBER OF ATOMS
        for i in range(max(0, atoms_start - 50), atoms_start):
            if lines[i].startswith("ITEM: NUMBER OF ATOMS") and i + 1 < len(lines):
                try:
                    return int(lines[i + 1].strip())
                except ValueError:
                    continue
        
        # Si no encontramos, contar líneas de datos
        logger.warning("NUMBER OF ATOMS no encontrado, contando líneas de datos")
        
        # Encontrar siguiente ITEM o final de archivo
        next_item = len(lines)
        for i in range(atoms_start + 1, len(lines)):
            if lines[i].startswith("ITEM:"):
                next_item = i
                break
        
        # Contar líneas no vacías
        data_lines = [line for line in lines[atoms_start + 1:next_item] 
                     if line.strip()]
        
        return len(data_lines)
    
    def _parse_atomic_data(self, lines: List[str], start_idx: int, 
                          n_atoms: int, columns: List[str]) -> pd.DataFrame:
        """Parsear datos atómicos en DataFrame"""
        data_rows = []
        lines_read = 0
        
        for i in range(start_idx, min(start_idx + n_atoms * 2, len(lines))):
            if lines_read >= n_atoms:
                break
                
            line = lines[i].strip()
            if not line or line.startswith("ITEM:"):
                continue
            
            parts = line.split()
            if len(parts) >= len(columns):
                try:
                    # Convertir a float, manejar NaN
                    row = []
                    for j, part in enumerate(parts[:len(columns)]):
                        try:
                            row.append(float(part))
                        except ValueError:
                            row.append(np.nan)
                    
                    data_rows.append(row)
                    lines_read += 1
                    
                except Exception as e:
                    logger.warning(f"Error parseando línea {i}: {line[:50]}...")
                    continue
        
        if not data_rows:
            return pd.DataFrame()
        
        df = pd.DataFrame(data_rows, columns=columns)
        
        # Limpiar valores infinitos
        df = df.replace([np.inf, -np.inf], np.nan)
        
        return df
    
    def find_dump_files(self, directory: str) -> List[str]:
        """Encontrar todos los archivos LAMMPS dump en un directorio"""
        directory_path = Path(directory)
        
        if not directory_path.exists():
            raise ValueError(f"Directorio no existe: {directory}")
        
        dump_files = []
        
        # Patrones de búsqueda
        patterns = [
            "*.dump", "*.dump.gz", 
            "dump.*", "dump.*.gz",
            "*.lammpstrj", "*.lammpstrj.gz"
        ]
        
        for pattern in patterns:
            dump_files.extend(directory_path.glob(pattern))
        
        # Eliminar duplicados y ordenar
        unique_files = list(set(dump_files))
        
        return sorted([str(f) for f in unique_files])
    
    def validate_dump_file(self, path: str) -> bool:
        """Validar que un archivo es un dump válido de LAMMPS"""
        try:
            with self._open_file(path) as f:
                # Leer primeras líneas para validar formato
                first_lines = [f.readline().strip() for _ in range(10)]
            
            # Buscar indicadores de archivo LAMMPS
            has_item = any(line.startswith("ITEM:") for line in first_lines)
            has_timestep = any("TIMESTEP" in line for line in first_lines)
            
            return has_item and has_timestep
            
        except Exception:
            return False