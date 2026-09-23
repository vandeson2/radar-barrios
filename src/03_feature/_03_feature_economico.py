
"""
 Calcular 6 features económicos por barrio

Features:
  1. renta_media_2023
  2. renta_mediana_2023
  3. cambio_renta_2022_2026 (4 años)
  4. categoria_renta (High/Medium/Low)
  5. desigualdad_gini (estimado)
  6. pct_poblacion_renta_baja

Datos disponibles: 2022-2026 (5 años)
Fuente: dataset_cleaned_renta.parquet
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

current_dir = Path(__file__).resolve()
for parent in current_dir.parents:
    if (parent / "config.py").exists():
        sys.path.insert(0, str(parent))
        break
from config import (PATHS, logger)
from _00_tabla_base import generar_base_barrios

def features_economico() -> pd.DataFrame:
    #  Cargar datos
    logger.info("\n Cargando datos...")
    df_renta = pd.read_parquet(PATHS["processed"]["cleaned"]["renta"])
    df_barrios = pd.read_parquet(PATHS["processed"]["cleaned"]["barrios"])
    df_base = generar_base_barrios()


    print(f"Renta: {df_renta.shape}")
    print(f"Base: {df_base.shape}")
    print(f"Barrios: {df_barrios.shape}\n")

    # Verificar períodos
    periodos = sorted(df_renta['Periodo'].unique())
    print(f"Períodos disponibles: {periodos}\n")

    # 2. PREPARAR RENTA
    logger.info("Preparando datos de renta...")

    # Extraer código de distrito: 
    df_renta['codigo_distrito'] = (
        df_renta['Distritos']
        .str.extract(r'distrito (\d+)', expand=False)
        .astype(int)
    )

    print(f"Distritos únicos: {df_renta['codigo_distrito'].nunique()}")
    print(f"Indicadores disponibles: {df_renta['Indicadores de renta media'].nunique()}\n")

    # SELECCIONAR AÑOS CLAVE
    logger.info("Seleccionando años clave...")

    # Pivotar para facilitar acceso
    def pivotar_renta(df_periodo):
        return df_periodo.pivot_table(
            index='codigo_distrito',
            columns='Indicadores de renta media',
            values='Total',
            aggfunc='first'
        )

    df_renta_2023 = df_renta[df_renta['Periodo'] == 2023]
    df_renta_2022 = df_renta[df_renta['Periodo'] == 2022]
    df_renta_2026 = df_renta[df_renta['Periodo'] == 2026]

    df_renta_2023_pivot = pivotar_renta(df_renta_2023)
    df_renta_2022_pivot = pivotar_renta(df_renta_2022)
    df_renta_2026_pivot = pivotar_renta(df_renta_2026)

    print(f"Registros 2023: {len(df_renta_2023)}")
    print(f"Registros 2022: {len(df_renta_2022)}")
    print(f"Registros 2026: {len(df_renta_2026)}\n")

    # CREAR MAPEO: barrio_id → codigo_distrito
    logger.info("Creando mapeo barrio_id → codigo_distrito...")

    # Usar COD_BAR para extraer distrito
    # COD_BAR en formato DDBB: 11 → distrito 1, 105 → distrito 1, 201 → distrito 2, etc
    df_barrios['codigo_distrito'] = (df_barrios['COD_BAR'] // 10).astype(int)

    # Crear diccionario de mapeo
    mapeo_barrio_distrito = dict(zip(df_barrios['COD_BAR'], df_barrios['codigo_distrito']))

    print(f"Mapeo creado: {len(mapeo_barrio_distrito)} barrios\n")

    # CALCULAR FEATURES ECONÓMICOS
    logger.info("Calculando features económicos...")

    features_list = []

    col_media = 'Media de la renta por unidad de consumo'
    col_mediana = 'Mediana de la renta por unidad de consumo'

    for _, row_base in df_base.iterrows():
        barrio_id = row_base['barrio_id']
        
        # Obtener código distrito
        codigo_dist = mapeo_barrio_distrito.get(barrio_id)
        
        if codigo_dist is None:
            features_list.append({
                'barrio_id': barrio_id,
                'renta_media_2023': 0.0,
                'renta_mediana_2023': 0.0,
                'cambio_renta_2022_2026': 0.0,
                'categoria_renta': 'Unknown',
                'desigualdad_gini': 0.0,
                'pct_poblacion_renta_baja': 0.0
            })
            continue
        
        # FEATURE 1: Renta media 2023
        try:
            renta_media = float(df_renta_2023_pivot.loc[codigo_dist, col_media])
        except (KeyError, TypeError):
            renta_media = 0.0
        
        # FEATURE 2: Renta mediana 2023
        try:
            renta_mediana = float(df_renta_2023_pivot.loc[codigo_dist, col_mediana])
        except (KeyError, TypeError):
            renta_mediana = 0.0
        
        # FEATURE 3: Cambio renta 2022-2026 (4 años)
        try:
            renta_media_2022 = float(df_renta_2022_pivot.loc[codigo_dist, col_media])
            renta_media_2026 = float(df_renta_2026_pivot.loc[codigo_dist, col_media])
            cambio_renta = ((renta_media_2026 - renta_media_2022) / renta_media_2022 * 100) if renta_media_2022 > 0 else 0.0
        except (KeyError, TypeError):
            cambio_renta = 0.0
        
        # FEATURE 4: Categoría renta (High/Medium/Low)
        if renta_media > 35:
            categoria = 'High'
        elif renta_media > 25:
            categoria = 'Medium'
        else:
            categoria = 'Low'
        
        # FEATURE 5: Desigualdad Gini (estimado como diferencia media-mediana)
        if renta_media > 0 and renta_mediana > 0:
            gini = abs(renta_media - renta_mediana) / renta_media
        else:
            gini = 0.0
        
        # FEATURE 6: % Población renta baja (estimado)
        if categoria == 'Low':
            pct_renta_baja = 40.0
        elif categoria == 'Medium':
            pct_renta_baja = 25.0
        else:
            pct_renta_baja = 10.0
        
        features_list.append({
            'barrio_id': barrio_id,
            'renta_media_2023': renta_media,
            'renta_mediana_2023': renta_mediana,
            'cambio_renta_2022_2026': float(cambio_renta),
            'categoria_renta': categoria,
            'desigualdad_gini': float(gini),
            'pct_poblacion_renta_baja': float(pct_renta_baja)
        })

    #CREAR DATAFRAME
    df_features_econ = pd.DataFrame(features_list)
    print(f"Features económicos creados: {df_features_econ.shape}\n")

   
    # VALIDACIÓN
    logger.info("\nVALIDACIÓN")
    logger.info(f"  Barrios: {len(df_features_econ)}")
    logger.info(f"  Barrios con renta: {(df_features_econ['renta_media_2023'] > 0).sum()}")
    logger.info(f"  Renta media promedio: {df_features_econ['renta_media_2023'].mean():.2f}k")
    logger.info(f"  Cambio renta 2022-2026: {df_features_econ['cambio_renta_2022_2026'].mean():.2f}%")
    logger.info(f"  Duplicados: {df_features_econ['barrio_id'].duplicated().sum()}")
    logger.info(f"  Nulos totales: {df_features_econ.isnull().sum().sum()}")

    return df_features_econ
