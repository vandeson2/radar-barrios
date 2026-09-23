"""
MÓDULO DE ENRIQUECIMIENTO: PRECIOS REGISTRADORES EN CAPA GOLD
==============================================================
Enriquece la Capa Gold agregando los precios medios por m2 por distrito
provenientes del Colegio de Registradores / TINSA.
"""

from pathlib import Path
import sys
import pandas as pd

# Mapeo completo Barrio -> Distrito
MAPEO_BARRIO_DISTRITO = {
    # Centro
    "Palacio": "Centro",
    "Embajadores": "Centro",
    "Cortes": "Centro",
    "Justicia": "Centro",
    "Universidad": "Centro",
    "Sol": "Centro",
    "Atocha": "Centro",
    "Latina": "Latina",
    # Retiro
    "Ibiza": "Retiro",
    "Los Jerónimos": "Retiro",
    "Recoletos": "Retiro",
    "Simancas": "Retiro",
    "La Concepción": "Retiro",
    "Quintana": "Retiro",
    "Pueblo Nuevo": "Retiro",
    "Pacífico": "Retiro",
    "Niño Jesús": "Retiro",
    "Estrella": "Retiro",
    "Numancia": "Retiro",
    "Atalaya": "Retiro",
    "Buenavista": "Retiro",
    "Adelfas": "Retiro",
    "Palos de la Frontera": "Retiro",
    "Los Cármenes": "Retiro",
    "Hellín": "Retiro",
    # Salamanca
    "Almagro": "Salamanca",
    "Goya": "Salamanca",
    "Fuente del Berro": "Salamanca",
    "Guindalera": "Salamanca",
    "Lista": "Salamanca",
    # Chamartín
    "El Viso": "Chamartín",
    "Castellana": "Chamartín",
    "Prosperidad": "Chamartín",
    # Chamberí
    "Bellas Vistas": "Chamberí",
    "Cuatro Caminos": "Chamberí",
    "Castillejos": "Chamberí",
    "Chamberí": "Chamberí",
    "Vallehermoso": "Chamberí",
    "Arapiles": "Chamberí",
    "Trafalgar": "Chamberí",
    "Gaztambide": "Chamberí",
    "Ríos Rosas": "Chamberí",
    "Los Rosales": "Chamberí",
    # Tetuán
    "Tetuán": "Tetuán",
    # Moncloa
    "Moncloa": "Moncloa",
    "Casa de Campo": "Moncloa",
    "Campamento": "Moncloa",
    "Argüelles": "Moncloa",
    "Ciudad Universitaria": "Moncloa",
    "Aravaca": "Moncloa",
    "Valdezarza": "Moncloa",
    "Valdemarín": "Moncloa",
    "Valdeacederas": "Moncloa",
    "Mirasierra": "Moncloa",
    "El Plantío": "Moncloa",
    "Cuatro Vientos": "Carabanchel",
    "El Goloso": "Fuencarral",
    "Pinar del Rey": "Fuencarral",
    "Corralejos": "Fuencarral",
    "Fuentelarreina": "Fuencarral",
    "La Paz": "San Blas",
    "Ventas": "San Blas",
    "Herrera": "Fuencarral",
    "Tobalina": "Fuencarral",
    "Pilar": "Fuencarral",
    "Valdefuentes": "Fuencarral",
    "Castilla": "Fuencarral",
    "Diente de Sierva": "Fuencarral",
    "Barrio del Puerto": "San Blas",
    "Manoteras": "Hortaleza",
    # Carabanchel
    "Aluche": "Carabanchel",
    "Imperial": "Carabanchel",
    "Acacias": "Carabanchel",
    "Chopera": "Carabanchel",
    "Legazpi": "Carabanchel",
    "Delicias": "Carabanchel",
    "Abrantes": "Carabanchel",
    "Portazgo": "Carabanchel",
    "Puerta Bonita": "Carabanchel",
    "Puerta del Ángel": "Carabanchel",
    "Opañel": "Carabanchel",
    "Pradolongo": "Carabanchel",
    "Zofío": "Carabanchel",
    "Moscardó": "Carabanchel",
    "Comillas": "Carabanchel",
    "San Cristóbal": "Carabanchel",
    "San Fermín": "Carabanchel",
    "San Diego": "Carabanchel",
    "San Juan Bautista": "Carabanchel",
    "San Pascual": "Carabanchel",
    "El Salvador": "Carabanchel",
    "Amposta": "Carabanchel",
    "Carabanchel": "Carabanchel",
    # Fuencarral-El Pardo
    "Fuencarral-El Pardo": "Fuencarral",
    "El Pardo": "Fuencarral",
    "Peñagrande": "Fuencarral",
    "Montecarmelo": "Fuencarral",
    "Las Tablas": "Fuencarral",
    "Sanchinarro": "Fuencarral",
    "Ciudad Jardín": "Fuencarral",
    "Hispanoamérica": "Fuencarral",
    "Nueva España": "Fuencarral",
    # Hortaleza
    "Hortaleza": "Hortaleza",
    "Berruguete": "Hortaleza",
    "Canillas": "Hortaleza",
    "Almenara": "Hortaleza",
    # Barajas
    "Canillejas": "Barajas",
    "San Blas": "San Blas",
    "Alameda de Osuna": "Barajas",
    "Casco Histórico de Barajas": "Barajas",
    "El Cañaveral": "Barajas",
    "Colina": "Barajas",
    "Costillares": "Barajas",
    "Arcos": "Barajas",
    "Aeropuerto": "Barajas",
    "Rosas": "Barajas",
    "Apóstol Santiago": "Barajas",
    # Moratalaz
    "Vinateros": "Moratalaz",
    "Moratalaz": "Moratalaz",
    "Pavones": "Moratalaz",
    "Horcajo": "Moratalaz",
    "Marroquina": "Moratalaz",
    "Media Legua": "Moratalaz",
    "Fontarrón": "Moratalaz",
    "Palomeras Bajas": "Moratalaz",
    "Palomeras Sureste": "Moratalaz",
    "Valdebernardo": "Moratalaz",
    "Valderrivas": "Moratalaz",
    "Rejas": "San Blas",
    "Piovera": "San Blas",
    "Timón": "Villaverde",
    # Puente de Vallecas
    "Puente de Vallecas": "Puente de Vallecas",
    "Entrevías": "Puente de Vallecas",
    # Villa de Vallecas
    "Vallecas": "Villa de Vallecas",
    "Ensanche de Vallecas": "Villa de Vallecas",
    "Casco Histórico de Vallecas": "Villa de Vallecas",
    "Santa Eugenia": "Villa de Vallecas",
    # Vicálvaro
    "Casco Histórico de Vicálvaro": "Vicálvaro",
    # Villaverde
    "Villaverde Alto": "Villaverde",
    "Villaverde Bajo": "Villaverde",
    "Palomas": "Villaverde",
    "Almendrales": "Villaverde",
    "Águilas": "Villaverde",
    "Ángeles": "Villaverde",
    "Vista Alegre": "Villaverde",
    # Usera
    "Usera": "Usera",
    "Orcasitas": "Usera",
    "Orcasur": "Usera",
    "Lucero": "Usera",
    "San Isidro": "Usera",
    "Butarque": "Usera",
    # Arganzuela
    "Arganzuela": "Arganzuela",
    # Ciudad Lineal
    "Pacifico": "Ciudad Lineal",
}


def enriquecer_precios(
    df_gold: pd.DataFrame,
    df_precios_raw: pd.DataFrame,
    col_barrio: str = "barrio_nombre",
) -> pd.DataFrame:
    """Enriquece el DataFrame de la Capa Gold agregando los precios de registradores

    asociados mediante el distrito del barrio.

    Parameters:
    df_gold : pd.DataFrame (Obligatorio)
    DataFrame de la Capa Gold a enriquecer.
    df_precios_raw : pd.DataFrame (Obligatorio)
    DataFrame con los precios por distrito.
    col_barrio : str, por defecto 'barrio_nombre'
    Nombre de la columna del barrio en df_gold.

Returns:

pd.DataFrame
    DataFrame df_gold con la nueva columna 'precio_m2_registradores' agregada.
"""
    if df_gold is None or df_gold.empty:
        raise ValueError("El DataFrame `df_gold` es obligatorio y no puede estar vacío.")

    if df_precios_raw is None or df_precios_raw.empty:
        raise ValueError("El DataFrame `df_precios_raw` es obligatorio.")

    if col_barrio not in df_gold.columns:
        raise KeyError(
            f"La columna '{col_barrio}' no se encuentra en la Capa Gold."
        )

    df_out = df_gold.copy()
    df_p = df_precios_raw.copy()

    # Normalizar columna distrito en precios
    if "distrito" not in df_p.columns:
        col_dist = [c for c in df_p.columns if "distri" in c.lower()]
        if col_dist:
            df_p = df_p.rename(columns={col_dist[0]: "distrito"})
        else:
            raise KeyError("No se encontró la columna 'distrito' en el dataset de precios.")

    # Filtrar por el año más reciente si existe
    if "año" in df_p.columns:
        df_p = df_p[df_p["año"] == df_p["año"].max()]

    # Buscar columna de precio m2
    col_precio = None
    for c in ["precio_m2_eur", "precio_m2", "precio_m2_registradores"]:
        if c in df_p.columns:
            col_precio = c
            break

    if col_precio is None:
        raise KeyError("No se encontró la columna con el valor de precio por m2.")

    df_p_sub = df_p[["distrito", col_precio]].rename(
        columns={col_precio: "precio_m2_registradores"}
    ).drop_duplicates(subset=["distrito"])

    # Asignar distrito en df_gold si no lo tiene
    if "distrito" not in df_out.columns:
        df_out["distrito"] = df_out[col_barrio].map(MAPEO_BARRIO_DISTRITO)

    # Hacer Merge conservando todos los registros y columnas de df_gold
    df_out = df_out.merge(df_p_sub, on="distrito", how="left")

    # Imputar con la mediana si algún distrito/barrio no tuvo match
    if df_out["precio_m2_registradores"].isna().sum() > 0:
        mediana = df_out["precio_m2_registradores"].median()
        df_out["precio_m2_registradores"] = df_out["precio_m2_registradores"].fillna(mediana)

    return df_out