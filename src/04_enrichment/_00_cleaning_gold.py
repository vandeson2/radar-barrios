import pandas as pd
import numpy as np
from pathlib import Path
import sys

current_dir = Path(__file__).resolve()
for parent in current_dir.parents:
    if (parent / "config.py").exists():
        sys.path.insert(0, str(parent))
        break
from config import logger

def limpiar_capa_gold(df_gold: pd.DataFrame) -> pd.DataFrame:
    """Limpia la Capa Gold, elimina multicolinealidad y filtra barrios

    problemáticos.

    (El escalado con StandardScaler se realiza en la etapa de train/test para
    evitar Data Leakage).

    Param:
        df_gold: DataFrame de la Capa Gold cruda.

    Returns:
        df_limpio: DataFrame procesado y listo para splitting/ML.
    """
    df_limpio = df_gold.copy()
    print(f"Original: {df_limpio.shape}\n")

    # 1. IDENTIFICAR BARRIOS PROBLEMÁTICOS
    logger.info("Identificando barrios problemáticos...")
    problematicos = df_limpio[
        (df_limpio["poblacion_total"] == 0)
        | (df_limpio["edad_media"] == 0)
        | (df_limpio["zona"] == "Unknown")
    ]
    print(f"Barrios problemáticos: {len(problematicos)}")
    if len(problematicos) > 0:
        print(
            problematicos[
                [
                    "barrio_id",
                    "barrio_nombre",
                    "poblacion_total",
                    "edad_media",
                    "zona",
                ]
            ]
        )

    # 2. ELIMINAR MULTICOLINEALIDAD
    logger.info("\nEliminando features con multicolinealidad...")
    columnas_eliminar = [
        "cambio_acumulado_pct",  # Correlación 1.0 con velocidad_crecimiento_anual
        "densidad_poblacional",  # Correlación 1.0 con poblacion_total
        "media_movil_12m",  # Correlación 1.0 con n_bares_202606
        "crecimiento_poblacion_anual",  # Correlación 0.997 con proximidad_estaciones_metro
    ]
    cols_a_borrar = [c for c in columnas_eliminar if c in df_limpio.columns]
    df_limpio = df_limpio.drop(columns=cols_a_borrar)

    # 3. ELIMINAR BARRIOS PROBLEMÁTICOS
    logger.info("Manejando barrios problemáticos...")
    if len(problematicos) > 0:
        df_limpio = df_limpio[
            ~df_limpio["barrio_id"].isin(problematicos["barrio_id"])
        ]
        logger.info(f"Barrios eliminados: {len(problematicos)}")
        logger.info(f"Después de eliminar: {df_limpio.shape}\n")

    # 4. VERIFICAR RESULTADO
    logger.info("Verificando resultado final...")
    print(f"CAPA GOLD LIMPIA")
    print(f"  Filas: {len(df_limpio)}")
    print(f"  Columnas: {len(df_limpio.columns)}")
    print(f"  Nulos: {df_limpio.isnull().sum().sum()}")
    print(f"  Duplicados: {df_limpio['barrio_id'].duplicated().sum()}")

    print(f"\nTARGET FINAL")
    print(f"  NO (0): {(df_limpio['gentrificara'] == 0).sum()}")
    print(f"  SÍ (1): {(df_limpio['gentrificara'] == 1).sum()}")
    print(
        f"  Desbalance: {(df_limpio['gentrificara'] == 0).sum() / (df_limpio['gentrificara'] == 1).sum():.2f}:1"
    )

    print(f"\nCOLUMNAS FINALES: {len(df_limpio.columns)}]")
    for i, col in enumerate(df_limpio.columns, 1):
        print(f"  {i:2d}. {col}")

    """   
        # 7. GUARDAR CAPA GOLD LIMPIA
    logger.info("\n[7] Guardando CAPA GOLD LIMPIA...")

    output_parquet = 'data/gold/gold_barrios_completo_limpio.parquet'
    output_csv = 'data/goldgold_barrios_completo_limpio.csv'

    df_limpio.to_parquet(output_parquet, index=False)
    df_limpio.to_csv(output_csv, index=False)

    logger.info(f" Guardado: {output_parquet}")
    logger.info(f" Guardado: {output_csv}")

    # 8. GUARDAR METADATOS DE NORMALIZACIÓN
    logger.info("\n[8] Guardando información de normalización...")
"""
    return df_limpio
