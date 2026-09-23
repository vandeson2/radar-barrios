import pandas as pd
from difflib import SequenceMatcher
from pathlib import Path
import sys


current_dir = Path(__file__).resolve()
for parent in current_dir.parents:
    if (parent / "config.py").exists():
        sys.path.insert(0, str(parent))
        break
from config import (PROCESSED_PATHS, logger)

def normalizar(s):
    """Normaliza string: strip + uppercase + sin acentos"""
    return (
        s.str.strip()
        .str.upper()
        .str.replace('Á', 'A', regex=False)
        .str.replace('É', 'E', regex=False)
        .str.replace('Í', 'I', regex=False)
        .str.replace('Ó', 'O', regex=False)
        .str.replace('Ú', 'U', regex=False)
        .str.replace('Ñ', 'N', regex=False)
    )

def mapear_barrios_fuzzy(
        df_cons: pd.DataFrame,
        df_barrios: pd.DataFrame,
        umbral_similitud: float = 0.75,
) -> pd.DataFrame:
    """FUNCIÓN PURA PARA PIPELINE:

    Recibe los DataFrames de consolidado y catálogo de barrios, realiza un
    fuzzy matching y devuelve un DataFrame enriquecido con el mapeo.
    """
    logger.info("Normalizando descripciones de barrios para fuzzy matching...")
    mapeo_cons = (
        df_cons[["id_barrio_local", "desc_barrio_local"]]
        .drop_duplicates()
        .sort_values("id_barrio_local")
        .copy()
    )

    mapeo_cons['desc_norm'] = normalizar(mapeo_cons['desc_barrio_local'])
    df_barrios = df_barrios.copy()
    df_barrios['nom_norm'] = normalizar(df_barrios['NOMBRE'])
    logger.info("Ejecutando fuzzy matching (similitud >0.75)...\n")

    mapeo_final = []
    sin_match = []

    for _, row_cons in mapeo_cons.iterrows():
        id_barrio = row_cons['id_barrio_local']
        desc_cons = row_cons['desc_norm']
        
        # Buscar mejores matches
        mejores = []
        for _, row_barrio in df_barrios.iterrows():
            nom_barrio = row_barrio['nom_norm']
            similitud = SequenceMatcher(None, desc_cons, nom_barrio).ratio()
            if similitud > umbral_similitud:
                mejores.append((similitud, row_barrio['COD_BAR'], nom_barrio))
        
        if mejores:
            similitud, cod_bar, nom_match = max(mejores)
            mapeo_final.append({
                'id_barrio_local': id_barrio,
                'desc_barrio_consolidado': row_cons['desc_barrio_local'],
                'COD_BAR': cod_bar,
                'nombre_barrio': nom_match,
                'similitud': round(similitud, 3)
            })
        else:
            sin_match.append({
                'id_barrio_local': id_barrio,
                'desc_barrio_consolidado': row_cons['desc_barrio_local']
            })
        logger.info(f" {id_barrio}: '{desc_cons}' → SIN MATCH")

    df_mapeo = pd.DataFrame(mapeo_final)
    return df_mapeo
