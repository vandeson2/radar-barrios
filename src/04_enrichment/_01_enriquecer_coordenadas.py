import logging
import pandas as pd

logger = logging.getLogger(__name__)


def enriquecer_coordenadas(
    df_gold: pd.DataFrame, df_coords: pd.DataFrame
) -> pd.DataFrame:
    """Enriquece el DataFrame de la Capa Gold añadiendo coordenadas a partir del

    nombre del barrio.

    Param:
        df_gold: DataFrame de la Capa Gold limpia.
        df_coords: DataFrame con las coordenadas (latitud, longitud,
          barrio_nombre).

    Returns:
        df_merged: DataFrame enriquecido con coordenadas.
    """
    df_merged = df_gold.merge(
        df_coords, how="left", left_on="barrio_nombre", right_on="barrio_nombre"
    )

    # Validar coordenadas faltantes
    if "latitud" in df_merged.columns:
        nulos = df_merged["latitud"].isna().sum()
        if nulos > 0:
            sin_coords = df_merged[df_merged["latitud"].isna()][
                "barrio_nombre"
            ].tolist()
            logger.warning(
                f"{nulos} barrios sin coordenadas: {sin_coords[:5]}..."
            )

    return df_merged
