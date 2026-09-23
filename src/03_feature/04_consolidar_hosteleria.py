import pandas as pd
import numpy as np
from pathlib import Path
import sys
import gc

current_dir = Path(__file__).resolve()
for parent in current_dir.parents:
    if (parent / "config.py").exists():
        sys.path.insert(0, str(parent))
        break

from config import PROCESSED_PATHS,ANIOS_PROCESAR, DATA_PROCESSED, logger

def consolidar_hosteleria():
    """Consolida los 5 archivos anuales en uno solo"""
    
    print("=" * 80)
    print("CONSOLIDANDO HOSTELERÍA (TU ESTRUCTURA)")
    print("=" * 80)
    
    archivos_por_anio = {}
    for anio in ANIOS_PROCESAR:
        key = f"cleaned_{anio}"
        if key in PROCESSED_PATHS:
            archivos_por_anio[anio] = PROCESSED_PATHS[key]

    if not archivos_por_anio: 
        logger.error("No se encontraron las claves")
        return None
    
    # Verificar que existen
    logger.info("\n Verificando archivos...")
    archvios_validos = {}
    for anio, ruta in archivos_por_anio.items():
        if ruta.exists():
            tamanio_mb = ruta.stat().st_size / (1024 * 1024)
            logger.info(f"- {anio}: {ruta.name} ({tamanio_mb:.1f} MB)")
            archvios_validos[anio] = ruta
        else:
            logger.warning(f"- {anio}: NO ENCONTRADO - {ruta}")
    if not archvios_validos:
        logger.error("No hay archivos válidos disponibles")
        return None
        
    
    # Cargar y procesar 
    logger.info("\nCargando datos...")
    dataframes = []
    
    for anio, ruta in archvios_validos.items():
        logger.info(f"Cargando {anio}...")

        try:
            df = pd.read_parquet(ruta)
        
            # Normalizar columna de  fech
            if 'fecha' not in df.columns:
                df['fecha'] = pd.to_datetime(f'{anio}-01-01')
                logger.warning(f"  Agregada columna 'fecha' ({anio})")
            else:
                try:
                    df['fecha'] = pd.to_datetime(df['fecha'], format='%Y%m', errors='coerce')
                except:
                    df['fecha'] = pd.to_datetime(df['fecha'], format='mixed', errors='coerce')
    
            logger.info(f"- Dimensión: {df.shape}")       
            dataframes.append(df)

        except Exception as e:
            logger.error(f"Error al leer {ruta.name}: {e}")
        finally:
            gc.collect()

    if not dataframes:
        logger.error("No se puede caragr ningún DataFrame.")
    
    # Concatenar
    logger.info(f"\nConcatenando {len(dataframes)} archivos...")
    df_consolidado = pd.concat(dataframes, ignore_index=True)
    logger.info(f"Consolidado: {df_consolidado.shape}")
    del dataframes
    gc.collect()

    # Limpiar general
    logger.info(f"\nLimpiando datos...")
    
    # Duplicados
    columnas_clave = []
    
    if 'local_id' in df_consolidado.columns:
        columnas_clave.append('local_id')
        logger.info(f"Encontrado: 'local_id'")
    
    if 'fecha' in df_consolidado.columns:
        columnas_clave.append('fecha')
        logger.info(f"Encontrado: 'fecha'")
    
    if columnas_clave:
        logger.info(f"\nRemoviendo duplicados por columnas clave: {columnas_clave}")
        antes = len(df_consolidado)
        
        try:
            # Drop_duplicates SOLO por local_id + fecha (combinación única)
            df_consolidado = df_consolidado.drop_duplicates(subset=columnas_clave, keep='first')
            despues = len(df_consolidado)
            logger.info(f"Duplicados eliminados: {antes - despues}")
        except MemoryError:
            logger.warning(f"No hay suficiente memoria para deduplicar. Saltando...")
            logger.info(f"Procesando {len(df_consolidado)} registros sin deduplicar")
        except Exception as e:
            logger.warning(f"Error al deduplicar: {e}. Continuando...")
    else:
        logger.warning("se encontraron columnas clave para deduplicar")
        logger.info("Continuando sin deduplicar...")
    
    gc.collect()
    
    # Nulos
    nulos_total = df_consolidado.isnull().sum().sum()
    logger.info(f"Valores nulos totales: {nulos_total}")
    

# Información del barrio
    if 'id_barrio_local' in df_consolidado.columns:
        n_barrios = df_consolidado['id_barrio_local'].nunique()
        logger.info(f"Barrios únicos: {n_barrios}")
    
    # Información de fechas
    if 'fecha' in df_consolidado.columns:
        fecha_min = df_consolidado['fecha'].min()
        fecha_max = df_consolidado['fecha'].max()
        logger.info(f"Rango fechas: {fecha_min} a {fecha_max}")
    
    # Guardar
    output_path = PROCESSED_PATHS.get(
        "cleaned",
        DATA_PROCESSED / "02_cleaned" / "dataset_consolidado_all_years.parquet"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"\nGuardando dataset consolidado en: {output_path}")
    df_consolidado.to_parquet(output_path)
    logger.info("Guardado completdo con éxito.")

    try:
        df_consolidado = pd.read_parquet(output_path)
        logger.info(f"Verificación exitosa | Forma final: {df_consolidado.shape}")
    except Exception as e:
        logger.error(f" Falló la verificación del archivo guardado: {e}")

    return df_consolidado


if __name__ == "__main__":
    consolidar_hosteleria()
