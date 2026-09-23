from pathlib import Path
import pandas as pd
import sys

current_dir = Path(__file__).resolve()
for parent in current_dir.parents:
    if (parent / "config.py").exists():
        sys.path.insert(0, str(parent))
        break

from config import (
    logger
)


def limpiar_padron(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia el dataset de Padrón Municipal.
    
    Operaciones:
      1. Eliminar filas con nulos en código
      2. Eliminar columnas de metadatos (FX_*)
      3. Convertir código a int64
    
    Args:
        df (pd.DataFrame): Dataset de Padrón original
    
    Returns:
        pd.DataFrame: Dataset limpio (12 columnas)
    """
    
    logger.info(" INICIANDO LIMPIEZA PADRÓN MUNICIPAL")

    filas_inicio = len(df) 
    df = df.copy()

    #  Elimina filas con nulos críticos
    logger.info("\nEliminando filas con nulos...")
    df = df.dropna(subset=['COD_DIST_SECCION', 'COD_SECCION'])
    filas_eliminadas = filas_inicio - len(df)
    logger.info(f"Filas eliminadas: {filas_eliminadas:,}") 

    # Eliminando columnas metadatos
    logger.info("\nEliminando columnas de metadatos (FX_*)...")
    columnas_eliminar = ['FX_CARGA', 'FX_DATOS_INI', 'FX_DATOS_FIN']
    df = df.drop(columns=[col for col in columnas_eliminar if col in df.columns])
    logger.info(f"Columnas eliminadas: {len(columnas_eliminar)}")

    #  Convertir tipos de datos
    logger.info("\nConvertiendo tipos de datos...")
    df['COD_DIST_SECCION'] = df['COD_DIST_SECCION'].astype('int64')
    df['COD_SECCION'] = df['COD_SECCION'].astype('int64')
    logger.info("Códigos convertido a int64")

    logger.info("\n" + "="*80)
    logger.info(f"PADRÓN LIMPIO: {len(df):,} filas × {df.shape[1]} columnas")
    logger.info("="*80 + "\n")

    return df

def limpiar_renta(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia el dataset de Indicadores de Renta.
    
    Operaciones:
      1. Filtrar solo Madrid capital (21 distritos)
      2. Eliminar municipios externos
      3. Convertir Total de STR a FLOAT
      4. Eliminar registros con Total nulo
      5. Agregación a nivel DISTRITO
      6. Forward fill para 2024-2026
    
    Args:
        df (pd.DataFrame): Dataset de Renta original
    
    Returns:
        pd.DataFrame: Dataset limpio, agregado y con forward fill
    """
    
    logger.info("INICIANDO LIMPIEZA INDICADORES DE RENTA")
    df = df.copy()
    
    # Filtrar solo Madrid capital
    logger.info("\nFiltrando solo Madrid capital...")
    df = df.dropna(subset=['Distritos'])
    df = df[df['Distritos'].str.startswith('28079', na=False)]
    logger.info(f"  Distritos: {df['Distritos'].nunique()}")

    # Convertir Total a float
    logger.info("\nConvertiendo Total a float...")
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
    df = df.dropna(subset=['Total'])
    logger.info(f"Valores nulos eliminados")

    # Agregar a nivel distrito
    logger.info("\nAgregando a nivel distrito...")
    df = df.groupby(['Distritos', 'Indicadores de renta media', 'Periodo'], as_index=False)['Total'].mean()
    logger.info(f"Registros después agregación: {len(df):,}")

    # Forward fill 2024-2026 usando 2023
    logger.info("\nAplicando forward fill (2024-2026)...")
    df_2023 = df[df['Periodo'] == 2023].copy()
    forward_fill = []
    for año in [2024, 2025, 2026]:
        df_año = df_2023.copy()
        df_año['Periodo'] = año
        forward_fill.append(df_año)
    
    df = pd.concat([df] + forward_fill, ignore_index=True)
    df = df[df['Periodo'] >= 2022].reset_index(drop=True)
    logger.info(f"Forward fill completado: 2022-2026")

    # Columnas finales
    df = df[['Distritos', 'Indicadores de renta media', 'Periodo', 'Total']]

    # Resumen
    logger.info("\n" + "="*80)
    logger.info(f"RENTA LIMPIA: {len(df):,} filas × {df.shape[1]} columnas")
    logger.info("="*80 + "\n")
    
    return df
    

   

def limpiar_precios(df: pd.DataFrame):
    """
    Limpia el dataset de Precios Históricos.
    
    Operaciones:
      1. Eliminar columnas de metadatos innecesarios
    
    Args:
        df (pd.DataFrame): Dataset de Precios original
    
    Returns:
        pd.DataFrame: Dataset limpio (6 columnas)
    """
    logger.info("INICIANDO LIMPIEZA PRECIOS HISTÓRICOS")

    df = df.copy()

    # Eliminar metadatos
    logger.info("\nEliminando metadatos...")
    columnas_eliminar = ['fuente', 'fecha_actualizacion']
    df = df.drop(columns=[col for col in columnas_eliminar if col in df.columns])
    logger.info(f"  Columnas eliminadas: {len(columnas_eliminar)}")
    
    # Resumen
    logger.info("\n" + "="*80)
    logger.info(f"PRECIOS LIMPIOS: {len(df):,} filas × {df.shape[1]} columnas")
    logger.info("="*80 + "\n")
    
    return df

def limpiar_barrios(df: pd.DataFrame):
    """
    Limpia el dataset de Barrios.
    
    Operaciones:
      1. Eliminar columnas redundantes/derivadas
      2. Mantener solo 5 columnas esenciales
    
    Args:
        df (pd.DataFrame): Dataset de Barrios original
    
    Returns:
        pd.DataFrame: Dataset limpio (5 columnas)
    """
    logger.info(" INICIANDO LIMPIEZA BARRIOS")
    df = df.copy()

    # Mantener solo esenciales
    logger.info("\nEliminando columnas redundantes...")
    columnas_mantener = ['CODDIS', 'NOMDIS', 'COD_BAR', 'NOMBRE', 'Area']
    columnas_eliminar = [col for col in df.columns if col not in columnas_mantener]
    logger.info(f"  Columnas eliminadas: {len(columnas_eliminar)}")
    
    df = df[columnas_mantener]

    logger.info("\nNormalizando nombres de barrios...")
    df['barrio_nombre_norm'] = (
        df['NOMBRE']
        .str.strip()
        .str.upper()
        .str.replace('Á', 'A', regex=False)
        .str.replace('É', 'E', regex=False)
        .str.replace('Í', 'I', regex=False)
        .str.replace('Ó', 'O', regex=False)
        .str.replace('Ú', 'U', regex=False)
        .str.replace('Ñ', 'N', regex=False)
    )
    logger.info(f"Nombres normalizados: OK")
    
    # Resumen
    logger.info("\n" + "="*80)
    logger.info(f"BARRIOS LIMPIOS: {len(df):,} filas × {df.shape[1]} columnas")
    logger.info("="*80 + "\n")
    
    return df