import pandas as pd
from pathlib import Path
import sys

current_dir = Path(__file__).resolve()
for parent in current_dir.parents:
    if (parent / "config.py").exists():
        sys.path.insert(0, str(parent))
        break
from config import (PATHS, logger)

def generar_base_barrios () -> pd.DataFrame:
    """
   Genera tabla base de barrios con ID y nombre
    
    Input: dataset_cleaned_barrios.parquet
    
    Output: DataFrame con columnas: barrio_id, barrio_nombre
    
    Returns:
        pd.DataFrame: Base de barrios (128 × 2)
    """
    logger.info("Generando base de barrios...")
    logger.info("\nCargando barrios...")
    df_barrios = pd.read_parquet(PATHS["processed"]["cleaned"]["barrios"])
  
    #Selocciona y renombra columnas
    logger.info("\nSeleccionando columnas...")
    df_base =df_barrios[['COD_BAR','NOMBRE']].copy()
    df_base.columns = ['barrio_id', 'barrio_nombre']

    #Elimina duplicados
    df_base = df_base.drop_duplicates(subset=['barrio_id'])


    logger.info("\nVALIDACIÓN]")
    logger.info(f"  Total barrios: {len(df_base)}")
    logger.info(f"  Duplicados: {df_base['barrio_id'].duplicated().sum()}")
    logger.info(f"  Nulos en barrio_id: {df_base['barrio_id'].isnull().sum()}")
    logger.info(f"  Nulos en barrio_nombre: {df_base['barrio_nombre'].isnull().sum()}")

    return df_base
