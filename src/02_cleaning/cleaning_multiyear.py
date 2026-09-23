from pathlib import Path
import pandas as pd
import sys

current_dir = Path(__file__).resolve()
for parent in current_dir.parents:
    if (parent / "config.py").exists():
        sys.path.insert(0, str(parent))
        break

from config import (
    PALABRAS_HOSTELERIA,
    EPIGRAFES_HOSTELERIA,
    logger,
)

def limpiar_nulos(df: pd.DataFrame, anio:int) -> pd.DataFrame:
    """ Elimina columnas y filas con nulos"""
    logger.info(f"Limpiando nulos...")

    nulos_antes = df.isnull().sum().sum()

    # Eliminar duplicadas del merge
    cols_duplicadas = [col for col in df.columns
                       if (col.endswith('_x') or col.endswith('_y'))
                       and 'local' not in col.lower()]
    df = df.drop(columns=cols_duplicadas)

    # Eliminar filas sin coordenadas (TODOS los años)
    df = df.dropna(subset=['coordenada_x_local', 'coordenada_y_local'], how='any')
    logger.info(f"  Filas eliminadas sin coordenadas válidas")

    #Eliminar columnas con > 90% nulos
    cols_eliminar = [
        'hora_apertura2', 'hora_cierre2', 'hora_cierre1', 'hora_apertura1',
        'coordenada_x_agrupacion', 'coordenada_y_agrupacion',
        'id_agrupacion', 'nombre_agrupacion', 'id_tipo_agrup', 'desc_tipo_agrup',
        'id_local_agrupado', 'fx_carga_y', 'fx_datos_ini',
        'fx_datos_fin', 'fx_carga_x', 'coordenada_y_agrup_x', 'coordenada_y_agrup_y',
        'id_vial_edificio', 'id_vial_acceso', 'id_ndp_edificio', 'id_clase_ndp_edificio',
        'id_ndp_acceso', 'id_clase_ndp_acceso','secuencial_local_PC',
    ]
    cols_existentes = [col for col in cols_eliminar if col in df.columns]
    df = df.drop(columns=cols_existentes)
    logger.info(f"  Eliminadas {len(cols_existentes)} columnas con >90% nulos")

    #Eliminar filas sin BARRIOS o LOCAL_ID
    df = df.dropna(subset=['local_id', 'desc_barrio_local'], how='any')
    logger.info("Eliminadas filas sin barrio/local_id")

    if 'desc_epigrafe' in df.columns:
        df['desc_epigrafe'] = df['desc_epigrafe'].fillna('DESCONOCIDO')
        logger.info(f"  desc_epigrafe: rellenada con 'DESCONOCIDO'")

    # Imputar descripcion_actividad
    if 'descripcion_actividad' in df.columns:
        df['descripcion_actividad'] =df['descripcion_actividad'].replace(
            'NULO EN ORIGEN', 'DESCONOCIDO'
        )
        df['descripcion_actividad'] =df['descripcion_actividad'].fillna('DESCONOCIDO')

    # Imputar id_epigrafe
    if 'id_epigrafe' in df.columns:
        df['id_epigrafe'] = df['id_epigrafe'].fillna(0).astype('str')

    # Imputar nulos en fecha_apertura
    if 'fecha_apertura' in df.columns:
        df['fecha_apertura'] = df['fecha_apertura'].fillna(df['fecha'])
    logger.info(f"      fecha_apertura: imputada con fecha del mes")

    #Imputar nulos en codigo postal
    moda =df['cod_postal'].mode()[0] if not df['cod_postal'].mode().empty else '28000'
    df['cod_postal'] = df['cod_postal'].fillna(moda)
    logger.info("cod_postal imputado con 0")

    #Imputar rotulo
    df['rotulo'] = df['rotulo'].fillna('DESCONOCIDO')
    for col in ['id_seccion', 'desc_seccion', 'id_division', 'desc_division']:
        df[col] = df[col].fillna('DESCONOCIDA')

    nulos_despues = df.isnull().sum().sum()
    logger.info(f" Nulos antes: {nulos_antes:,} -> después {nulos_despues:,}")

    return df


def eliminar_duplicados(df: pd.DataFrame, anio: int) -> pd.DataFrame:
    """Eliminar duplicados exactos"""
    logger.info(" Eliminando duplicados...")

    filas_antes = len(df)
    df = df.drop_duplicates()
    filas_despues = len(df)



    if filas_antes > filas_despues:
        eliminadas = filas_antes - filas_despues
        logger.info(f" Duplicados exactos eliminados: {eliminadas:,}")

    return df


def normalizar_tipo(df: pd.DataFrame, anio: int) -> pd.DataFrame:
    """Normalizar tipos de datos"""
    logger.info(" Normalizando tipos...")

    # Convertir StringDtype a str
    string_cols = df.select_dtypes(include=['string']).columns
    for col in string_cols:
        df[col] =df[col].astype('str')

    if len(string_cols) > 0:
        logger.info(f"      StringDtype → str: {len(string_cols)} columnas")

    #IDs a int64
    id_cols = ['local_id', 'id_barrio_local', 'id_distrito_local']
    for col in id_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
            except Exception as e:
                logger.warning(f" No se puedo convertir: {col}: {e}")

    if 'id_epigrafe' in df.columns:
        df['id_epigrafe'] = df['id_epigrafe'].astype('str')



    #coordenadas a float
    coord_cols = ['coordenada_x_local', 'coordenada_y_local']
    for col in coord_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass

    return df

def limpiar_encoding(df: pd.DataFrame, anio: int) -> pd.DataFrame:
    """Limpiar carateres problematicos"""
    logger.info(" Limpiando encoding...")

    problemas_antes = 0

    #columnas principales con problema
    cols_criticas = ['rotulo', 'descripcion_actividad', 'desc_epigrafe', 'nombre_agrupacion']

    # limpiar columnas de texto
    for col in cols_criticas:
        if col in df.columns and df[col].dtype in ['object', 'string']:
            valores_str = df[col].astype(str)
            problemas = valores_str.str.contains('ï»¿|Ã|â€|Â', regex=True, na=False).sum()
            problemas_antes += problemas

            df[col] = df[col].str.replace('ï»¿', '', regex=False)
            df[col] = df[col].str.replace('Â', '', regex=False)
            df[col] = df[col].str.replace('â€', '', regex=False)
            df[col] = df[col].str.replace('Ã', '', regex=False)

            df[col] = df[col].str.upper()


    logger.info(f" Problemas de encoding limpiados: {problemas_antes}")

    return df


def crear_features_basicas(df: pd.DataFrame, anio: int) -> pd.DataFrame:
    """Crear columnas derivadas"""
    logger.info(" Creando features básicoas...")

    #Crear columnas es_hosteleria
    df['es_hosteleria'] = (
        df['descripcion_actividad'].str.upper().str.contains(
            '|'.join(PALABRAS_HOSTELERIA), na=False
        ) |
        df['id_epigrafe'].isin(EPIGRAFES_HOSTELERIA)
    )

    # año
    df['anio'] = anio
    logger.info(f" Hosteleria: {df['es_hosteleria'].sum():,}")

    return df
def seleccionar_columnas_necesarias(df: pd.DataFrame, anio: int) -> pd.DataFrame:
    """Elimina columnas innecesarias para ahorrar espacio"""
    logger.info(" Seleccionando columnas necesarias...")
    
    # Columnas a MANTENER
    columnas_necesarias = [
        'local_id',
        'id_barrio_local',
        'desc_barrio_local',
        'id_distrito_local',
        'desc_distrito_local',
        'fecha',
        'fecha_apertura',
        'coordenada_x_local',
        'coordenada_y_local',
        'descripcion_actividad',
        'es_hosteleria',
        'desc_division',
        'id_division',
        'id_epigrafe',
        'desc_epigrafe',
        'rotulo'
    ]
    
    # Filtrar solo columnas que existen
    cols_validas = [col for col in columnas_necesarias if col in df.columns]
    
    # Contar cuántas se eliminan
    cols_eliminadas = set(df.columns) - set(cols_validas)
    
    df = df[cols_validas]
    
    logger.info(f"  Columnas eliminadas: {len(cols_eliminadas)}")
    logger.info(f"  Columnas finales: {len(cols_validas)}")
    logger.info(f"  Reducción esperada: ~75%")
    
    return df

def normalizar_nombres(df: pd.DataFrame, anio: int) -> pd.DataFrame:
    """Normaliza nombres de barrios para joins posteriores"""
    logger.info(" Normalizando nombres de barrios...")
    
    # Crear versión normalizada: strip + uppercase
    df['barrio_nombre_norm'] = (
        df['desc_barrio_local']
        .str.strip()
        .str.upper()
        .str.replace('Á', 'A')
        .str.replace('É', 'E')
        .str.replace('Í', 'I')
        .str.replace('Ó', 'O')
        .str.replace('Ú', 'U')
        .str.replace('Ñ', 'N')
    )
    
    return df
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

def pipeline_limpieza(df: pd.DataFrame, anio: int) -> pd.DataFrame:
    """Pipeline de limpieza"""

    logger.info(f"Limpiando año {anio}")
    logger.info(f"  Antes: {len(df):,} filas, {df.shape[1]} columnas, {df.memory_usage(deep=True).sum() / (1024**2):.1f} MB")

    df = limpiar_nulos(df, anio)
    df = eliminar_duplicados(df, anio)
    df = normalizar_tipo(df, anio)
    df = limpiar_encoding(df, anio)
    df = normalizar_nombres(df, anio)
    df = crear_features_basicas(df, anio)
    df = seleccionar_columnas_necesarias(df,anio)

    logger.info(f"  Después: {len(df):,} filas, {df.shape[1]} columnas, {df.memory_usage(deep=True).sum() / (1024**2):.1f} MB")

    return df

