import pandas as pd
from difflib import SequenceMatcher
from pathlib import Path
import sys

current_dir = Path(__file__).resolve()
for parent in current_dir.parents:
    if (parent / "config.py").exists():
        sys.path.insert(0, str(parent))
        break
from config import logger

# Mapeo manual por defecto
MAPEO_MANUAL = {
    1901: 191,    # CASCO H.VICALVARO → Casco Histórico de Vicálvaro
    1801: 181,    # CASCO H.VALLECAS → Casco Histórico de Vallecas
    2103: 213,    # CASCO H.BARAJAS → Casco Histórico de Barajas
    1701: 165,    # SAN ANDRES → Apóstol Santiago
}

def completar_mapeo_manual(
    df_fuzzy: pd.DataFrame,
    mapeo_manual: dict = MAPEO_MANUAL,
    total_esperado: int=131,
) -> pd.DataFrame:
    """
    Combina el DataFrame generado por el fuzzy matching con un diccionario
    de mapeos manuales y devuelve el DataFrame consolidado.
    """
    logger.info("\n Combinando fuzzy + manual...")

    resultado = df_fuzzy[["id_barrio_local", "COD_BAR"]].copy()

    nuevos_manuales = []
    for id_cons, cod_bar in mapeo_manual.items():
        if id_cons not in resultado['id_barrio_local'].values:
            nuevos_manuales.append({'id_barrio_local': id_cons, 'COD_BAR': cod_bar})
            logger.info(f" Agregado: {id_cons} → {cod_bar}")

    if nuevos_manuales:
        df_nuevos = pd.DataFrame(nuevos_manuales)
        resultado = pd.concat([resultado, df_nuevos], ignore_index=True)

    resultado = resultado.sort_values('id_barrio_local').reset_index(drop=True)

    # validación interna
    duplicados = resultado["id_barrio_local"].duplicated().sum()
    nulos = resultado.isnull().sum().sum()
    total_obtenido = len(resultado)

    if duplicados > 0:
        logger.warning(
            f"Se encontraron {duplicados} identificadores duplicados en el mapeo."
        )
    if nulos > 0:
        logger.warning(f"Se encontraron {nulos} valores nulos en el mapeo.")

    if total_obtenido == total_esperado:
        logger.info(
            f" Cobertura perfecta: {total_esperado} barrios mapeados correctamente."
        )
    else:
        logger.warning(
            f" Cobertura incompleta: Se esperaban {total_esperado} barrios y se obtuvieron {total_obtenido}."
        )

    return resultado