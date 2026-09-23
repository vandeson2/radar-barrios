from pathlib import Path
import sys
import numpy as np
import pandas as pd


def enriquecer_capa_gold(
    df_gold: pd.DataFrame,
    df_precios: pd.DataFrame = None,
    df_metro: pd.DataFrame = None,
    col_barrio: str = "barrio_nombre",
) -> pd.DataFrame:
    """Aplica enriquecimiento de datos, feature engineering limpio e imputación

    de nulos a un DataFrame de la capa Gold.

    Parameters:
    df_gold : pd.DataFrame
    DataFrame base de la capa Gold.
    df_precios : pd.DataFrame, opcional
    DataFrame con información de precios registradores.
    df_metro : pd.DataFrame, opcional
    DataFrame con información de accesibilidad a Metro.
    col_barrio : str, por defecto 'barrio_nombre'
    Nombre de la columna utilizada como clave de unión.

    Returns:
    pd.DataFrame
    DataFrame enriquecido y procesado.
"""
    df_res = df_gold.copy()

    if col_barrio not in df_res.columns:
        raise KeyError(
            f"La columna '{col_barrio}' no se encuentra en el DataFrame Gold principal."
        )

    # Clave de cruce limpia (sin espacios extra)
    df_res["_key_clean"] = df_res[col_barrio].astype(str).str.strip()

    # 1. Integrar Precios
    if df_precios is not None and "precio_m2_registradores" in df_precios.columns:
        if col_barrio in df_precios.columns:
            df_p = df_precios.copy()
            df_p["_key_clean"] = df_p[col_barrio].astype(str).str.strip()
            df_p_sub = df_p[["_key_clean", "precio_m2_registradores"]].drop_duplicates(
                subset=["_key_clean"]
            )

            # Evitar columnas duplicadas (_x, _y)
            if "precio_m2_registradores" in df_res.columns:
                df_res = df_res.drop(columns=["precio_m2_registradores"])

            df_res = df_res.merge(df_p_sub, on="_key_clean", how="left")

        # 2. Integrar Metro
        cols_metro = [
            "distancia_metro_km",
            "tiempo_pie_a_metro_min",
            "accesibilidad_metro",
        ]
        if df_metro is not None and all(c in df_metro.columns for c in cols_metro):
            if col_barrio in df_metro.columns:
                df_m = df_metro.copy()
                df_m["_key_clean"] = df_m[col_barrio].astype(str).str.strip()
                df_m_sub = df_m[["_key_clean"] + cols_metro].drop_duplicates(
                    subset=["_key_clean"]
                )

            # Evitar columnas duplicadas
            for c in cols_metro:
                if c in df_res.columns:
                    df_res = df_res.drop(columns=[c])

            df_res = df_res.merge(df_m_sub, on="_key_clean", how="left")

        # Eliminar columna temporal de cruce
        df_res = df_res.drop(columns=["_key_clean"])

        # 3. Feature Engineering
        columnas_trend = [
            c
            for c in df_res.columns
            if "tendencia" in c.lower() or "cambio_renta" in c.lower()
        ]

        if len(columnas_trend) >= 2:
            df_res["trend_score"] = df_res[columnas_trend[:2]].mean(axis=1)

        # 4. Rellenar NaNs numéricos con la mediana
        numeric_cols = df_res.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df_res[col].isna().sum() > 0:
                median_val = df_res[col].median()
                df_res[col] = df_res[col].fillna(median_val)

    return df_res
def ejecutar_enriquecimiento_gold(
        ruta_gold: str = "data/gold/gold_barrios_con_coordenadas.parquet",
        rutas_precios: list = None,
        rutas_metro: list = None,
        ruta_salida: str = "data/gold/gold_barrios_enriquecido.parquet",
        ) -> pd.DataFrame:
        """Orquesta la lectura de archivos, invoca el enriquecimiento y guarda el resultado."""
        print("=" * 100)
        print("PASO 0: ENRIQUECIMIENTO DE LA CAPA GOLD (EJECUCIÓN DE FUNCIÓN)")
        print("=" * 100)

        # 1. Cargar GOLD Principal
        path_gold = Path(ruta_gold)
        if not path_gold.exists():
            print(f"No se encuentra el archivo principal: {ruta_gold}")
            sys.exit(1)

        df_gold = pd.read_parquet(path_gold)
        print(f"\n1. GOLD cargado: {len(df_gold)} barrios × {len(df_gold.columns)} columnas")

        # 2. Intentar cargar Precios (Fallback)
        if rutas_precios is None:
            rutas_precios = [
                "datos_precios_registradores_barrios.csv",
                "data/datos_precios_registradores_barrios.csv",
            ]

        df_precios = None
        for r in rutas_precios:
            p = Path(r)
            if p.exists():
                try:
                    df_precios = pd.read_csv(p)
                    print(f"2.Precios cargados desde '{r}': {len(df_precios)} registros")
                    break
                except Exception as e:
                    print(f"Error leyendo {r}: {str(e)[:30]}")

        if df_precios is None:
            print("2.Precios no encontrados (continuando sin ellos)")

        # 3. Intentar cargar Metro (Fallback)
        if rutas_metro is None:
            rutas_metro = [
                "datos_metro_barrios.csv",
                "data/datos_metro_barrios.csv",
            ]

        df_metro = None
        for r in rutas_metro:
            p = Path(r)
            if p.exists():
                try:
                    df_metro = pd.read_csv(p)
                    print(f"3. Metro cargado desde '{r}': {len(df_metro)} registros")
                    break
                except Exception as e:
                    print(f"  Error leyendo {r}: {str(e)[:30]}")

        if df_metro is None:
            print("3. Metro no encontrado (continuando sin él)")

        # 4. Procesar
        print("\n4. Procesando transformaciones y feature engineering...")
        df_resultado = enriquecer_capa_gold(
            df_gold=df_gold, df_precios=df_precios, df_metro=df_metro
        )

        # 5. Guardar
        path_out = Path(ruta_salida)
        path_out.parent.mkdir(parents=True, exist_ok=True)
        df_resultado.to_parquet(path_out, index=False)

        print(f"\nArchivo guardado exitosamente en: {ruta_salida}")
        print(
            f"Dimensiones finales: {len(df_resultado)} barrios × {len(df_resultado.columns)} columnas"
        )
        print(f"Datos faltantes restantes: {df_resultado.isna().sum().sum()}")
        print("=" * 100)

        return df_resultado
