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
from _01_feature_hosteleria import features_hosteleria
from _03_feature_economico import features_economico
def generar_target() -> pd.DataFrame:
    """
    Etiquetar target (gentrificara: 1=SÍ, 0=NO)

    Criterios:
    - SÍ (1): Malasaña, Chueca, Lavapiés, Rastro
    - NO (0): Vallecas, Villaverde, Carabanchel
    - Resto: Asignar basado en renta + hostelería

    Fuente: Validación manual + datos de renta/hostelería
    """
    #  Cargar datos
    logger.info("Generando target...")
    logger.info("\n Cargando datos...")
    df_base = generar_base_barrios()
    df_barrios = pd.read_parquet(PATHS["processed"]["cleaned"]["barrios"])
    df_host = features_hosteleria()
    df_econ = features_economico()

    print(f"Base: {df_base.shape}")
    print(f"Barrios: {df_barrios.shape}\n")

    # 2. DEFINIR ETIQUETADO MANUAL
    logger.info("Definiendo etiquetado manual...")

    # Barrios conocidos como gentrificados (SÍ = 1)
    BARRIOS_GENTRIFICADOS_NOMBRES = ['Malasaña', 'Chueca', 'Lavapiés', 'Rastro']

    # Barrios NO gentrificados (NO = 0)
    BARRIOS_NO_GENTRIFICADOS_NOMBRES = ['Vallecas', 'Villaverde', 'Carabanchel Viejo', 'Carabanchel']

    print(f"Gentrificados SÍ (1): {BARRIOS_GENTRIFICADOS_NOMBRES}")
    print(f"Gentrificados NO (0): {BARRIOS_NO_GENTRIFICADOS_NOMBRES}\n")

    # Crear diccionario de etiquetado manual
    etiquetado_manual = {}

    # Gentrificados SÍ
    for nombre in BARRIOS_GENTRIFICADOS_NOMBRES:
        barrio_match = df_barrios[df_barrios['NOMBRE'].str.contains(nombre, case=False, na=False)]
        for _, row in barrio_match.iterrows():
            etiquetado_manual[int(row['COD_BAR'])] = 1

    # Gentrificados NO
    for nombre in BARRIOS_NO_GENTRIFICADOS_NOMBRES:
        barrio_match = df_barrios[df_barrios['NOMBRE'].str.contains(nombre, case=False, na=False)]
        for _, row in barrio_match.iterrows():
            etiquetado_manual[int(row['COD_BAR'])] = 0

    print(f"Barrios etiquetados manualmente: {len(etiquetado_manual)}\n")

    # 3. CREAR FEATURE TARGET
    logger.info("Creando feature target...")

    features_list = []

    for _, row_base in df_base.iterrows():
        barrio_id = row_base['barrio_id']
        
        # Si está en etiquetado manual, usar ese
        if barrio_id in etiquetado_manual:
            gentrificara = etiquetado_manual[barrio_id]
            fuente = 'manual'
        else:
            # Si no, asignar basado en heurística: renta_media + cambio_renta + hostelería
            # Barrio con: renta alta + crecimiento + más bares = probable gentrificación
            
            host_row = df_host[df_host['barrio_id'] == barrio_id]
            econ_row = df_econ[df_econ['barrio_id'] == barrio_id]
            
            if len(host_row) == 0 or len(econ_row) == 0:
                gentrificara = 0  # Sin datos = asumir NO
                fuente = 'sin_datos'
            else:
                renta_media = float(econ_row['renta_media_2023'].values[0])
                cambio_renta = float(econ_row['cambio_renta_2022_2026'].values[0])
                n_bares = int(host_row['n_bares_202606'].values[0])
                velocidad_crecimiento = float(host_row['velocidad_crecimiento_anual'].values[0])
                
                # Heurística: Gentrificación = renta alta + bares + crecimiento
                score = 0
                
                # Renta media > 30k (High) = +1
                if renta_media > 30:
                    score += 1
                
                # Cambio renta > 5% = +1
                if cambio_renta > 5.1:
                    score += 1
                
                # Más de 150 bares = +1
                if n_bares > 150:
                    score += 1
                
                # Crecimiento hostelería > 2% anual = +1
                if velocidad_crecimiento > 0.02:
                    score += 1
                
                # Si score >= 3, probable gentrificación
                gentrificara = 1 if score >= 3 else 0
                fuente = f'heurística(score={score})'
        
        features_list.append({
            'barrio_id': barrio_id,
            'gentrificara': gentrificara,
            'fuente_etiquetado': fuente
        })

    # 4. CREAR DATAFRAME
    df_target = pd.DataFrame(features_list)
    print(f"Target creado: {df_target.shape}\n")


    # 6. VALIDACIÓN
    logger.info("\nVALIDACIÓN")
    logger.info(f"  Barrios: {len(df_target)}")
    logger.info(f"  Gentrificados SÍ (1): {(df_target['gentrificara'] == 1).sum()}")
    logger.info(f"  Gentrificados NO (0): {(df_target['gentrificara'] == 0).sum()}")
    logger.info(f"  Desbalance: {(df_target['gentrificara'] == 1).sum() / len(df_target) * 100:.1f}% SÍ")
    logger.info(f"  Etiquetados manualmente: {(df_target['fuente_etiquetado'] == 'manual').sum()}")
    logger.info(f"  Etiquetados por heurística: {(df_target['fuente_etiquetado'].str.contains('heurística')).sum()}")
    logger.info(f"  Duplicados: {df_target['barrio_id'].duplicated().sum()}")
    logger.info(f"  Nulos: {df_target.isnull().sum().sum()}")

    return df_target