# 🏘️ Radar de Barrio: Predictor de Gentrificación en Madrid

**Proyecto de Trabajo Final de Máster (TFM)**  
**Autor:** Vandeson Sena e Silva  
**Universidad:** [TU UNIVERSIDAD]  
**Año:** 2026

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Instalación](#instalación)
3. [Ejecución del Pipeline](#ejecución-del-pipeline)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Datos Utilizados](#datos-utilizados)
6. [Resultados Esperados](#resultados-esperados)
7. [Limitaciones y Caveats](#limitaciones-y-caveats)
8. [Referencias](#referencias)

---

## 📖 Descripción General

### Problema que Resuelve

Cada año en Madrid, **inversores, planificadores urbanos y ciudadanos toman decisiones de inversión sin información sistemática sobre cuáles barrios van a gentrificarse**. Las señales de gentrificación (explosión de bares modernos, llegada de población joven, cambios en comercio) emergen **meses antes** de que se reflejen en precios, pero nadie las conecta de forma rigurosa.

**Ejemplo real:** Malasaña pasó de €3,500/m² (2018) a €5,200/m² (2020), un aumento de **48% en 2 años**. Los que compraron en 2019 ganaron; los que esperaron demasiado, perdieron la oportunidad.

### Solución Planteada

**Radar de Barrio** es un **clasificador de Machine Learning** que predice si un barrio de Madrid gentrificará en los próximos **12-18 meses** basándose en:

- 📊 **54 meses de evolución comercial** (Feb 2022 - Jun 2026)
- 👥 **Contexto demográfico** (población, edad, diversidad)
- 💰 **Datos económicos** (renta media/mediana)
- 🌍 **Factores geográficos** (distancia centro, estaciones metro)
- 💵 **Validación con precios reales** (Colegio de Registradores/TINSA)

### Resultados Entregables

✅ **Clasificador ML Ensemble:** Predice SÍ/NO gentrificación con probabilidad (0-100%)  
✅ **Dashboard Interactivo:** Streamlit con mapa de Madrid coloreado  
✅ **Explicabilidad SHAP:** Top 3 factores por barrio  
✅ **Validación Rigurosa:** Correlación con precios oficiales (Registradores)  
✅ **Ranking TOP 10:** Barrios en riesgo inmediato  
✅ **Informes Exportables:** PDF profesional para presentar a inversores  

---

## 🚀 Instalación

### Requisitos Previos

- **Python 3.8+**
- **Git**
- **RAM:** 8+ GB recomendado
- **Espacio disco:** ~15 GB (datos raw + processed)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/radar-barrios.git
cd radar-barrios
```

### Paso 2: Crear Entorno Virtual

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Paso 3: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 4: Descargar Datos

Los datos se descargan automáticamente en el pipeline. Para descargarlos manualmente:

```bash
# Crear estructura de carpetas
mkdir -p data/raw/{2022,2023,2024,2025,2026} data/raw/otros

# Los datos deben estar en:
# - data/raw/YYYY/ : Censo de Locales (archivos CSV mensuales)
# - data/raw/otros/ : Padrón, Renta, Precios, Barrios
```

**Fuentes de datos públicas:**
- 📊 Censo Locales: https://datos.madrid.es/dataset/209548-0-censo-locales-historico
- 👥 Padrón Municipal: https://datos.madrid.es/dataset/200076-2-padron-municipal-csv
- 💰 Renta INE: Instituto Nacional de Estadística
- 🏠 Precios Registradores: Colegio de Registradores
- 🗺️ Límites Barrios: https://datos.madrid.es/dataset/300496-0-barrios-madrid

---

## ⚙️ Ejecución del Pipeline

### Opción A: Pipeline Completo (40-50 minutos)

```bash
# 1. Cargar datos raw (54 meses, ~9M registros)
python src/01_data/01_data_loading.py
# Output: data/processed/consolidated_*.parquet

# 2. Limpiar datos (valores nulos, duplicados, outliers)
python src/02_cleaning/03_cleaning_main.py
# Output: data/processed/cleaned/*.parquet

# 3. Ingeniería de features + Capa Gold (128 barrios × 32 columnas)
python src/03_feature/_06_capa_gold.py
# Output: data/gold/gold_barrios_completo.parquet

# 4. Entrenar modelo ML (Ensemble: SVM + RF + GB)
python src/05_ml_training/train.py
# Output: data/04_train_test/modelo_ensemble_v2_mejorado.pkl

# 5. Ejecutar Dashboard
streamlit run src/06_dashboard/pr.py
# Abre: http://localhost:8501
```

### Opción B: Dashboard Directo (si ya existe modelo)

```bash
# Ejecutar solo el dashboard (carga modelo pre-entrenado)
streamlit run src/06_dashboard/pr.py
```

### Opciones de Ejecución

```bash
# Dashboard en desarrollo (hot reload)
streamlit run src/06_dashboard/pr.py --logger.level=debug

# Dashboard en producción
streamlit run src/06_dashboard/pr.py --logger.level=error
```

---

## 📁 Estructura del Proyecto

```
radar-barrios/
├── README.md                          # Este archivo
├── requirements.txt                   # Dependencias Python
├── config.py                          # Configuración centralizada
│
├── docs/entregas/                     # Directrices académicas
│   ├── 01_ideas_producto.md
│   ├── 02_datos_necesarios.md
│   ├── 03_modelo_datos.md
│   ├── 04_analisis_modelado.md
│   └── 05_diseño_frontal.md
│
├── src/                               # Código fuente (pipeline + dashboard)
│   ├── 01_data/                       # Carga de datos raw
│   │   ├── 01_data_loading.py         # Consolidación de 54 meses
│   │   └── harmonizar_columnas.py
│   │
│   ├── 02_cleaning/                   # Limpieza y normalización
│   │   ├── 03_cleaning_main.py
│   │   ├── cleaning_multiyear.py
│   │   └── cleaning_complementarios.py
│   │
│   ├── 03_feature/                    # Ingeniería de features
│   │   ├── _00_tabla_base.py          # Base: 128 barrios
│   │   ├── _01_feature_hosteleria.py  # 10 features (velocidad, aceleración, etc)
│   │   ├── _02_feature_demografico.py # 8 features (población, edad, etc)
│   │   ├── _03_feature_economico.py   # 6 features (renta, desigualdad, etc)
│   │   ├── _04_feature_geografico.py  # 3 features (distancia, metro, zona)
│   │   ├── _05_target.py              # Etiquetado manual (gentrificara: 0/1)
│   │   ├── _06_capa_gold.py           # Tabla final: 128×32 columnas
│   │   └── mapeo/                     # Mapeo barrios fuzzy
│   │
│   ├── 04_enrichment/                 # Enriquecimiento de datos
│   │   ├── _00_cleaning_gold.py
│   │   ├── _01_enriquecer_coordenadas.py
│   │   ├── _02_enriquecer_precios.py
│   │   ├── _03_enriquecer_distancia_metro.py
│   │   ├── _04_enriquecer_gold.py
│   │   └── _05_pipeline_enriquecimiento.py
│   │
│   ├── 05_ml_training/                # Entrenamiento y evaluación
│   │   ├── train.py                   # Versión final (Ensemble)
│   │   ├── train_v1_baseline.py
│   │   ├── generar_feature_names.py
│   │   └── 5_optimizar_mejorado_final.py
│   │
│   ├── 06_dashboard/                  # Frontend Streamlit
│   │   └── pr.py                      # Dashboard interactivo (+1400 líneas)
│   │
│   └── visualization/                 # Visualizaciones
│       └── __init__.py
│
├── notebooks/                         # Análisis exploratorio (16 notebooks)
│   ├── 01_eda_exploratory.ipynb
│   ├── 02_eda_after_cleaned.ipynb
│   ├── 03_Feature_Importance_SHAP.ipynb
│   ├── 04_eda_explo_barrios.ipynb
│   └── ... (más análisis)
│
├── data/                              # Datos en capas
│   ├── raw/                           # Raw sin procesar (~10 GB)
│   │   ├── 2022-2026/                 # 54 meses mensuales
│   │   └── otros/                     # Padrón, Renta, Precios, Barrios
│   │
│   ├── processed/                     # Datos limpios y procesados (~3 GB)
│   │   ├── 01_consolidated/
│   │   ├── 02_cleaned/
│   │   ├── 03_engineered/
│   │   └── 04_train_test/
│   │
│   └── gold/                          # Datos finales (capa gold)
│       ├── gold_barrios_completo.parquet (128×32)
│       ├── gold_barrios_predicciones.csv
│       └── gold_validacion_registradores.csv
│
├── models/                            # Modelos entrenados
│   ├── logistic_regression.pkl
│   ├── svm_model.pkl
│   ├── xgboost_model.pkl
│   ├── modelo_ensemble_v2_mejorado.pkl
│   └── scaler.pkl
│
├── logs/                              # Logs de ejecución
│   └── pipeline.log
│
└── reports/                           # Reportes y análisis
    ├── feature_importance.png
    ├── confusion_matrix.png
    └── roc_curve.png
```

---

## 📊 Datos Utilizados

### Fuentes Principales

| Fuente | Cobertura | Granularidad | Registros |
|--------|-----------|--------------|-----------|
| **Censo de Locales** | Feb 2022 - Jun 2026 (54m) | Barrio | 9M+ (149k locales únicos) |
| **Padrón Municipal** | Jul 2026 (snapshot) | Sección censal → Barrio | 128 barrios |
| **Renta (INE)** | 2015-2023 (8 años) | Sección censal → Barrio | 128 barrios |
| **Registradores/TINSA** | 2024+ (snapshot) | Barrio | 154 barrios ⭐ |
| **Precios Idealista** | May 2025 - Apr 2026 (12m) | Distrito | 21 zonas |
| **Límites Barrios** | Estático | GeoJSON | 131 barrios |

### Validación de Datos

✅ **Calidad:** Datos oficiales, públicos, sin barreras de acceso  
✅ **Completitud:** 54 meses continuos (Feb 2022 - Jun 2026)  
✅ **Limpieza:** Valores nulos, duplicados, outliers manejados  
✅ **Consistencia:** Validación de estructura y tipos de datos  

---

## 📈 Resultados Esperados

### Modelo ML

| Métrica | Objetivo | Estado |
|---------|----------|--------|
| **F1-Score** | > 0.75 | ✅ Cumple |
| **Precision** | > 0.70 | ✅ Cumple |
| **Recall** | > 0.70 | ✅ Cumple |
| **AUC-ROC** | > 0.80 | ✅ Cumple |
| **Estabilidad CV** | Std < 0.05 | ✅ Cumple |

### Salida del Dashboard

**Para cada barrio de Madrid:**

```
VALLECAS - 🔴 ALTO RIESGO
├─ Probabilidad: 87%
├─ Top 3 Factores:
│  ├─ Crecimiento Hostelería: +42%
│  ├─ Renta Mediana Baja: €18.000/año
│  └─ Población Joven: +18% menores de 30
├─ Validación (Registradores):
│  ├─ Precio actual: €5.200/m²
│  ├─ Cambio 3 años: +26%
│  └─ Análisis: ✅ VALIDADO
└─ Barrios similares: Lavapiés (89%), Rastro (85%)
```

### Archivos de Salida

```
outputs/
├── gold_barrios_predicciones.csv         # Ranking TOP 10-15
├── gold_validacion_registradores.csv     # Correlación ML vs precios
├── mapa_madrid_predicciones.html         # Mapa interactivo
├── feature_importance.png                # Importancia de features
├── shap_analysis.png                     # Análisis SHAP
└── reporte_ejecutivo.pdf                 # Informe profesional
```

---

## ⚠️ Limitaciones y Caveats

### Limitaciones de Datos

1. **Target Etiquetado Manualmente**
   - Solo 4-5 barrios etiquetados explícitamente (Malasaña, Chueca, Lavapiés, Rastro)
   - Resto estimado por patrones similares
   - Validado con Registradores (r > 0.60)

2. **Padrón es Snapshot (No Serie Temporal)**
   - Solo tenemos datos de Jul 2026
   - Feature `crecimiento_poblacion_anual` es estimado
   - No captura cambios demográficos en tiempo real

3. **Renta Antigua (2023)**
   - Datos de 3 años atrás
   - Asumo que ranking de barrios (pobre vs rico) es estable
   - Cambios recientes no visibles

4. **Precios Limitados (12 Meses)**
   - Histórico Idealista: solo May 2025 - Apr 2026
   - Registradores: snapshot actual (mejor para validación)
   - Insuficiente para regresión temporal

### Limitaciones del Modelo

1. **Desbalance de Clases**
   - 85% barrios NO gentrificados, 15% SÍ
   - Mitigado con `class_weight='balanced'` + SMOTE
   - Recall de clase positiva puede ser bajo

2. **Bajo Número de Muestras**
   - Solo 128 barrios (pequeño para ML moderno)
   - 30 features → ratio 4.3:1 muestras:features
   - Validación cruzada es crítica (5-fold)

3. **Definición de "Gentrificación" es Compleja**
   - Usamos proxy: explosión hostelería + renta baja + población joven
   - Realidad es multifactorial
   - Modelo captura una dimensión, no el fenómeno completo

4. **Sin Data Leakage, pero...**
   - Características basadas en observaciones pasadas
   - No captura cambios políticos repentinos (ley de vivienda)
   - No anticipa shocks económicos externos

### Lo que el Modelo NO Predice

❌ Cambios políticos (regulaciones de alquiler)  
❌ Eventos externos (pandemias, guerras)  
❌ Inversión en infraestructura (metro nuevo)  
❌ Cambios demográficos extremos (inmigración masiva)  
❌ Burbujas especulativas (booms/crashes)  

---

## 🔍 Guía de Uso (Usuario Final)

### Para Inversores

```python
# 1. Abrir dashboard
streamlit run src/06_dashboard/pr.py

# 2. Seleccionar barrio en el mapa (ej: Vallecas)

# 3. Ver:
#    - Probabilidad de gentrificación (87%)
#    - Top 3 factores (hostelería, renta, población)
#    - Precio actual Registradores (€5.200/m²)
#    - Validación (precios suben como predijo)

# 4. Comparar con barrios similares
#    - Lavapiés (89%, gentrificado 2018-2020)
#    - Rastro (85%, gentrificado 2019-2021)

# 5. Exportar PDF para junta de inversores
#    [📥 Exportar informe PDF]
```

### Para Planificadores Urbanos

```python
# 1. Ver ranking TOP 10 barrios en riesgo
#    - Vallecas (87%), Lavapiés (89%), Rastro (85%), ...

# 2. Identificar dónde intervenir urgentemente
#    - Barrios con alto riesgo + baja renta

# 3. Datos sólidos para justificar políticas
#    - 54 meses de histórico + validación Registradores

# 4. Visualización espacial (mapa coloreado)
#    - Rojo = Alto riesgo, Amarillo = Medio, Verde = Bajo
```

---

## 📚 Referencias Técnicas

### Documentación del Proyecto

- **02_datos_necesarios.md** → Análisis de viabilidad + inventario de fuentes
- **03_modelo_datos.md** → Estructura de capas + diccionario de datos
- **04_analisis_modelado.md** → Estrategia de validación + riesgos
- **05_diseño_frontal.md** → UX/UI del dashboard

### Librerías Principales

- **pandas** (2.0+) → Procesamiento de datos
- **scikit-learn** (1.3+) → Modelos ML
- **xgboost** (2.0+) → Gradient Boosting
- **streamlit** (1.30+) → Dashboard
- **folium** (0.14+) → Mapas interactivos
- **shap** (0.42+) → Explicabilidad
- **plotly** (5.17+) → Gráficos interactivos

### Papers y Metodologías

- [SHAP: A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874)
- [Gentrification and Neighborhood Change](https://www.jstor.org/stable/41058701)
- [Machine Learning for Urban Analytics](https://doi.org/10.1186/s42408-019-0005-6)

---

## 🤝 Contribuciones y Licencia

### Cómo Contribuir

Este es un proyecto académico (TFM). Para sugerencias o mejoras:

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/mi-mejora`
3. Commit: `git commit -m "Descripción del cambio"`
4. Push: `git push origin feature/mi-mejora`
5. Abre un Pull Request

### Licencia

MIT License - Ver LICENSE.md para detalles

---

## 📧 Contacto

**Autor:** Vandeson Sena e Silva  
**Email:** vandeson2@gmail.com  
**GitHub:** [tu-usuario/radar-barrios](https://github.com)

---

## 🙏 Agradecimientos

- **Ayuntamiento de Madrid** - Datos públicos (Censo Locales, Padrón, Barrios)
- **INE** - Indicadores de Renta
- **Colegio de Registradores** - Precios TINSA
- **Comunidad de Data Science** - Librerías y metodologías

---

**Última actualización:** 2026-09-21  
**Versión:** 1.0 (TFM Final)
