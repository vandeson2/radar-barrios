"""
Script para harmonizar columnas entre años ANTES de limpiar
Esto asegura que todos los años tengan el MISMO conjunto de columnas
"""

import pandas as pd
from pathlib import Path
import sys

current_dir = Path(__file__).resolve()
for parent in current_dir.parents:
    if (parent / "config.py").exists():
        sys.path.insert(0, str(parent))
        break

from config import PROCESSED_PATHS, ANIOS_PROCESAR, logger

def obtener_todas_columnas():
    """Obtiene el conjunto completo de columnas de todos los años"""
    
    print("\n" + "=" * 100)
    print("🔍 IDENTIFICANDO COLUMNAS POR AÑO")
    print("=" * 100)
    
    todas_columnas = set()
    columnas_por_anio = {}
    
    for anio in ANIOS_PROCESAR:
        try:
            df = pd.read_parquet(PROCESSED_PATHS[f"consolidated_{anio}"])
            columnas = set(df.columns)
            columnas_por_anio[anio] = columnas
            todas_columnas.update(columnas)
            
            print(f"\n{anio}: {len(columnas)} columnas")
            print(f"  {sorted(columnas)[:5]}... (mostrando primeras 5)")
            
        except Exception as e:
            print(f"❌ Error al leer {anio}: {e}")
    
    print(f"\n{'─' * 100}")
    print(f"✅ TOTAL COLUMNAS ÚNICAS (unión de todos los años): {len(todas_columnas)}")
    print(f"\nColumnas faltantes por año:")
    print(f"{'─' * 100}")
    
    for anio in sorted(ANIOS_PROCESAR):
        if anio in columnas_por_anio:
            faltantes = todas_columnas - columnas_por_anio[anio]
            if faltantes:
                print(f"\n{anio}: Faltan {len(faltantes)} columnas")
                print(f"  {sorted(faltantes)}")
            else:
                print(f"\n{anio}: ✅ Completo (tiene todas)")
    
    return todas_columnas, columnas_por_anio


def harmonizar_columnas():
    """Harmoniza columnas y sobrescribe los consolidated"""
    
    print("\n" + "=" * 100)
    print("🔧 HARMONIZANDO COLUMNAS")
    print("=" * 100)
    
    todas_columnas, columnas_por_anio = obtener_todas_columnas()
    todas_columnas_lista = sorted(list(todas_columnas))
    
    print(f"\n{'─' * 100}")
    print(f"Agregando columnas faltantes a cada año...")
    print(f"{'─' * 100}")
    
    for anio in ANIOS_PROCESAR:
        try:
            # Cargar
            ruta_input = PROCESSED_PATHS[f"consolidated_{anio}"]
            df = pd.read_parquet(ruta_input)
            
            print(f"\n{anio}:")
            print(f"  Antes: {df.shape[1]} columnas")
            
            # Identificar faltantes
            columnas_faltantes = set(todas_columnas_lista) - set(df.columns)
            
            # Agregar columnas faltantes con NaN
            for col in columnas_faltantes:
                df[col] = None
            
            # Reordenar para que tengan el MISMO ORDEN
            df = df[todas_columnas_lista]
            
            print(f"  Después: {df.shape[1]} columnas")
            if columnas_faltantes:
                print(f"  Columnas agregadas: {sorted(columnas_faltantes)}")
            
            # Guardar (sobrescribir)
            df.to_parquet(ruta_input, index=False)
            print(f"  ✅ Guardado con columnas harmonizadas")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n{'=' * 100}")
    print("✅ HARMONIZACIÓN COMPLETADA")
    print(f"Todos los años tienen {len(todas_columnas_lista)} columnas en el mismo orden")
    print(f"{'=' * 100}\n")


if __name__ == "__main__":
    harmonizar_columnas()

