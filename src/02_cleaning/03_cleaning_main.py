import pandas as pd
import sys
import gc
from pathlib import Path
from datetime import datetime


current_dir = Path(__file__).resolve()
for parent in current_dir.parents:
    if (parent / "config.py").exists():
        sys.path.insert(0, str(parent))
        break

from cleaning_complementarios import (
    limpiar_padron, limpiar_renta, limpiar_precios, limpiar_barrios
)
from cleaning_multiyear import pipeline_limpieza
from config import PROCESSED_PATHS, ANIOS_PROCESAR, logger


DATASETS_COMPLEMENTARIOS = [
    {
        'nombre': 'PADRÓN MUNICIPAL',
        'key_entrada': 'consolidated_padron',
        'key_salida': 'cleaned_padron',
        'funcion': limpiar_padron,
    },
    {
        'nombre': 'INDICADORES RENTA',
        'key_entrada': 'consolidated_renta',
        'key_salida': 'cleaned_renta',
        'funcion': limpiar_renta,
    },
    {
        'nombre': 'PRECIOS HISTÓRICOS',
        'key_entrada': 'consolidated_precios',
        'key_salida': 'cleaned_precios',
        'funcion': limpiar_precios,
    },
    {
        'nombre': 'BARRIOS',
        'key_entrada': 'consolidated_barrios',
        'key_salida': 'cleaned_barrios',
        'funcion': limpiar_barrios,
    },
]

def main():
    """Ejecutar limpieza: complementarios + hostelería multiyear."""
    
    logger.info("\n" + "="*80)
    logger.info(" INICIANDO LIMPIEZA COMPLETA")
    logger.info("="*80)
    
    inicio_total = datetime.now()
    
    # =========================================================================
    # FASE 1: COMPLEMENTARIOS
    # =========================================================================
    
    logger.info("\n FASE 1: COMPLEMENTARIOS")
    logger.info("-"*80)

    datasets_ok = 0
    datasets_error = 0
    
    for dataset in DATASETS_COMPLEMENTARIOS:
        try:
            # Cargar
            df = pd.read_parquet(PROCESSED_PATHS[dataset['key_entrada']])
            
            # Limpiar
            df_clean = dataset['funcion'](df)
            
            # Guardar
            output_path = Path(PROCESSED_PATHS[dataset['key_salida']])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df_clean.to_parquet(output_path, index=False)
            
            datasets_ok += 1
            
            # Liberar memoria
            del df, df_clean
            gc.collect()
            
        except Exception as e:
            logger.error(f" Error en {dataset['nombre']}: {e}")
            datasets_error += 1
            gc.collect()

    # =========================================================================
    # FASE 2: HOSTELERÍA MULTIYEAR
    # =========================================================================
    anios_procesados = 0
    anios_fallidos = 0
    
    for anio in ANIOS_PROCESAR:
        try:
            df = pd.read_parquet(PROCESSED_PATHS[f"consolidated_{anio}"])
            df_clean = pipeline_limpieza(df, anio)
            
            # Crear directorio si no existe
            output_dir = Path("data/processed/02_cleaned")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Guardar uno por año
            output = output_dir / f"dataset_cleaned_{anio}.parquet"
            df_clean.to_parquet(output, index=False)
            
            logger.info(f"    Guardado: {output}\n")
            anios_procesados += 1

            #  LIBERAR MEMORIA EXPLÍCITAMENTE
            del df
            del df_clean
            gc.collect()
            
        except Exception as e:
            logger.error(f" Error en {anio}: {e}\n")
            anios_fallidos += 1

            # Liberar memoria incluso si hay error
            gc.collect()
            continue
            continue
    
    logger.info("="*80)
    logger.info(f"LIMPIEZA COMPLETADA")
    logger.info(f"Años procesados: {anios_procesados}/{len(ANIOS_PROCESAR)}")
    if anios_fallidos > 0:
        logger.warning(f"Años con error: {anios_fallidos}")
    logger.info("="*80 + "\n")
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    
    tiempo_total = (datetime.now() - inicio_total).total_seconds()
    
    logger.info("\n" + "="*80)
    logger.info("LIMPIEZA COMPLETADA")
    logger.info("="*80)
    
    logger.info(f"\nCOMPLEMENTARIOS: {datasets_ok}/{len(DATASETS_COMPLEMENTARIOS)} exitosos")
    if datasets_error > 0:
       logger.warning(f"    {datasets_error} errores")
    
   # if HOSTELERIA_DISPONIBLE:
    logger.info(f"HOSTELERÍA: {anios_procesados}/{len(ANIOS_PROCESAR)} exitosos")
    if anios_fallidos > 0:
        logger.warning(f"{anios_fallidos} errores")
    
    logger.info(f"\nTiempo total: {tiempo_total:.2f}s")
    logger.info("="*80 + "\n")

if __name__ == "__main__":
    main()
