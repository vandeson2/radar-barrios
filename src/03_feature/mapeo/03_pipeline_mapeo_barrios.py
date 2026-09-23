"""
PIPELINE DE MAPEO COMPLETO
=========================
Orquesta el Fuzzy Matching y la adición de Mapeos Manuales para generar 
el archivo mapeo_barrios_final.parquet en la capa Gold.
"""

from pathlib import Path
import sys
import time
import pandas as pd

# ------------------------------------------------------------------------
# Detección y adición dinámica de la raíz del proyecto al sys.path
# ------------------------------------------------------------------------
current_dir = Path(__file__).resolve()
for parent in current_dir.parents:
    if (parent / "config.py").exists():
        sys.path.insert(0, str(parent))
        break

from config import PATHS, logger


def cargar_funcion_modulo(ruta_script: str, nombre_funcion: str):
    """Carga dinámicamente funciones de archivos Python locales."""
    import importlib.util

    path_script = Path(ruta_script).resolve()
    if not path_script.exists():
        raise FileNotFoundError(
            f"No se encuentra el script requerido: {ruta_script}"
        )

    spec = importlib.util.spec_from_file_location(
        path_script.stem, path_script
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

    if not hasattr(modulo, nombre_funcion):
        raise AttributeError(
            f"La función '{nombre_funcion}' no existe en {ruta_script}"
        )

    return getattr(modulo, nombre_funcion)


def ejecutar_pipeline_mapeo_barrios(
    ruta_output: Path | str = PATHS["gold"]["mapeo_barrios"]
) -> pd.DataFrame:
    """Ejecuta los dos pasos de mapeo en orden (Fuzzy -> Manual)

    y genera el archivo mapeo_barrios_final.parquet en la capa Gold.
    """
    start_time = time.time()
    logger.info("=" * 80)
    logger.info("INICIANDO PIPELINE DE MAPEO COMPLETO DE BARRIOS")
    logger.info("=" * 80)

    # ------------------------------------------------------------------------
    # 1. CARGA DE DATASETS BASE
    # ------------------------------------------------------------------------
    logger.info("\nCARGANDO DATASETS BASE")
    try:
        df_cons = pd.read_parquet(PATHS["processed"]["cleaned"]["hosteleria_consolidado"])
        df_barrios = pd.read_parquet(PATHS["processed"]["cleaned"]["barrios"])
        logger.info(f"Consolidado cargado: {df_cons.shape}")
        logger.info(f"Catálogo de barrios cargado: {df_barrios.shape}")
    except Exception as e:
        logger.error(
            f"Error crítico al leer datasets de entrada: {e}", exc_info=True
        )
        sys.exit(1)

    # ------------------------------------------------------------------------
    # 2. EJECUCIÓN SECUENCIAL EN MEMORIA (FUZZY + MANUAL)
    # ------------------------------------------------------------------------
    logger.info("\nEJECUTANDO MAPEOS (FUZZY + MANUAL)")
    try:
        # Importar funciones puras de los submódulos
        mapear_barrios_fuzzy = cargar_funcion_modulo(
            "src/03_feature/mapeo/_01_mapear_barrios_fuzzy.py",
            "mapear_barrios_fuzzy",
        )
        completar_mapeo_manual = cargar_funcion_modulo(
            "src/03_feature/mapeo/_02_mapeo_final.py",
            "completar_mapeo_manual",
        )

        # 2.1 Fuzzy Matching
        logger.info("Ejecutando Fuzzy Matching...")
        df_fuzzy = mapear_barrios_fuzzy(
            df_cons, df_barrios, umbral_similitud=0.75
        )

        # 2.2 Agregar Mapeos Manuales
        logger.info("Agregando Mapeos Manuales...")
        df_final = completar_mapeo_manual(df_fuzzy)

    except Exception as e:
        logger.error(
            f"Error crítico durante las transformaciones de mapeo: {e}",
            exc_info=True,
        )
        sys.exit(1)

    # ------------------------------------------------------------------------
    # 3. GENERACIÓN DEL ARCHIVO FINAL GOLD
    # ------------------------------------------------------------------------
    logger.info("\nGUARDANDO ARCHIVO FINAL MAPEO BARRIOS")
    try:
        path_output = Path(ruta_output)
        path_output.parent.mkdir(parents=True, exist_ok=True)

        # Guardar en Parquet (Capa Gold)
        df_final.to_parquet(path_output, index=False)
        logger.info(
            f" Archivo final generado exitosamente en: {path_output.resolve()}"
        )

    except Exception as e:
        logger.error(
            f"Error crítico al guardar el archivo de salida: {e}", exc_info=True
        )
        sys.exit(1)

    # ------------------------------------------------------------------------
    # RESUMEN Y FINALIZACIÓN
    # ------------------------------------------------------------------------
    elapsed_time = time.time() - start_time
    logger.info("=" * 80)
    logger.info("PIPELINE DE MAPEO COMPLETADO EXITOSAMENTE")
    logger.info(f"Tiempo total de ejecución: {elapsed_time:.2f} segundos")
    logger.info(f" Total Mappings generados: {len(df_final)}")
    logger.info("=" * 80)

    return df_final


if __name__ == "__main__":
    ejecutar_pipeline_mapeo_barrios()