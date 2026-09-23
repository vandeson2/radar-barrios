# Entrega 3 - Diseño del Modelo de Datos y Capa Gold

**Proyecto:** Predictor de Gentrificación - Clasificador ML
**Estudiante:** Vandeson Sena e Silva
---

## 1. Resumen de la Idea y Datos del Proyecto

### Problema y Solución

Mi proyecto construye un **clasificador de Machine Learning** que predice si un barrio de Madrid gentrificará en los próximos 12 meses. El clasificador responde a una pregunta binaria: **¿Este barrio gentrificará? SÍ / NO**

El problema que resuelvo es que inversores, planificadores urbanos y ciudadanos **no ven venir la gentrificación** antes de que los precios exploten. Las señales están presentes meses antes (explosión de bares modernos, llegada de población joven), pero nadie las conecta sistemáticamente.

### Fuentes de Datos Principales (ACTUALIZADO)

| Fuente | Cobertura | Granularidad | Uso en Modelo | Prioridad |
|--------|-----------|--------------|---|---|
| **Censo de Locales** | Feb 2022 - Jun 2026 (54 meses) | Barrio | Features principales (hostelería) | 🔴 CRÍTICA |
| **Padrón Municipal** | Jul 2026 (snapshot) | Sección censal → Barrio | Contexto demográfico | 🟠 ALTA |
| **Renta (INE)** | 2015-2023 (8 años) | Sección censal → Barrio | Feature + Etiquetado | 🟠 ALTA |
| **Registradores/TINSA** | 2024+ (snapshot) | **154 barrios (1:1)** | ⭐ **Validación PRIMARIA** | 🔴 CRÍTICA |
| **Precios Idealista** | May 2025 - Apr 2026 (12 meses) | Distrito | Validación secundaria | 🟢 BAJA |
| **Límites Barrios** | Estático | Geometrías de 131 barrios | Visualización en mapa | 🟢 BAJA |

**Cambio principal:** Registradores/TINSA sustituye a Idealista como **validación primaria**
- Granularidad: Barrio (vs distrito anterior)
- Fuente: Oficial registral (vs estimaciones de portal)
- Confiabilidad: Máxima (vs media anterior)

El **objetivo final** es un clasificador que tome 25-30 features de evolución comercial y contexto demográfico, y prediga para cada barrio si gentrificará. **Validado rigurosa con Registradores (154 barrios).**

---

## 2. Tecnología o Formato de Almacenamiento Elegido

### Decisión: Combinación de Parquet + CSV + Pickle

**Justificación:**

1. **Parquet para datos procesados (capa processed y gold)**
   - Eficiente en almacenamiento.
   - Preserva tipos de datos nativamente.
   - Optimizado para Python/Pandas/ML (ecosistema scikit-learn)
   - Soporte nativo para compresión.
   - Mejor rendimiento que CSV para lectura iterativa.

2. **CSV para datos raw y exportación**
   - Descarga directa de datos.madrid.es (ya están en CSV)
   - Formato estándar, auditable (puedo abrir en Excel/editor de texto)
   - Trazabilidad completa de transformaciones
   - Compatibilidad universal

3. **Pickle para modelos entrenados**
   - Guardar modelos XGBoost, scaler, etc para predicción futura
   - Preserva objetos Python complejos
   - Carga rápida en fase de inferencia

---

## 3. Estructura de Capas de Datos (ACTUALIZADO)

```
data/
├── raw/
│   ├── 2022-2026/
│   │   ├── censo_actividades_2022_02.csv
│   │   ├── censo_actividades_2022_03.csv
│   │   ├── ... (52 archivos mensuales más)
│   │   └── censo_actividades_2026_06.csv
│   │
│   └── otros/
│       ├── padron_municipal_2026_07.csv
│       ├── renta_ine_2015_2023.csv
│       ├── precios_idealista_2025_2026.csv
│       ├── datos_precios_registradores_barrios.csv ⭐ NUEVO
│       └── limites_barrios_madrid.geojson
│
├── processed/
│   ├── 01_consolidated/
│   │   └── dataset_54_meses_consolidado.parquet (1GB)
│   │
│   ├── 02_cleaned/
│   │   ├── censo_actividades_limpio.parquet (800MB)
│   │   ├── padron_agregado_barrio.parquet (5MB)
│   │   ├── renta_agregado_barrio.parquet (2MB)
│   │   ├── precios_registradores_barrio.parquet (1MB) ⭐ NUEVO
│   │   └── precios_idealista_agregado_distrito.parquet (1MB)
│   │
│   ├── 03_engineered/
│   │   ├── features_hosteleria.parquet (50MB)
│   │   ├── features_demograficas.parquet (3MB)
│   │   ├── features_economicas.parquet (2MB)
│   │   └── dataset_con_features.parquet (100MB)
│   │
│   └── 04_train_test/
│       ├── X_train.parquet (80MB)
│       ├── X_test.parquet (20MB)
│       ├── y_train.parquet (500KB)
│       └── y_test.parquet (100KB)
│
└── gold/
    ├── gold_barrios_completo.parquet (150MB - LA TABLA PRINCIPAL)
    ├── gold_barrios_predicciones.csv (50KB - ranking de predicciones)
    ├── gold_validacion_registradores.csv ⭐ NUEVO (validación primaria)
    └── gold_validacion_idealista.csv (validación secundaria)
```

**Cambios principales:**
- ✅ Agregado: `datos_precios_registradores_barrios.csv` en raw/otros
- ✅ Agregado: `precios_registradores_barrio.parquet` en processed/02_cleaned
- ✅ Agregado: `gold_validacion_registradores.csv` (nueva métrica de validación)
- ✅ Renombrado: `gold_validacion_precios.csv` → `gold_validacion_idealista.csv`

models/
├── logistic_regression.pkl
├── svm_model.pkl
├── xgboost_model.pkl (mejor modelo)
└── scaler.pkl (normalizador)
```
---

## 4. Definición de la Capa Gold 

### Dataset Principal: `gold_barrios_completo.parquet`

**Descripción funcional:**
Tabla consolidada de 128 barrios de Madrid con 30+ features de evolución comercial, contexto demográfico y variable target (SÍ/NO gentrificará). Es el dataset que alimentará directamente el clasificador ML.

**Granularidad:**
- **Una fila por barrio** (128 filas totales)
- **Columnas:** 1 ID barrio + 30 features + 1 target

**Número aproximado de registros:**
- 128 barrios (datos Madrid)
- Esperado: 128 filas × 32 columnas

**Campos Principales:**

#### Identificadores (Obligatorios)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `barrio_id` | int | Código único del barrio (1-128) |
| `barrio_nombre` | str | Nombre del barrio (Malasaña, Chueca, etc) |

#### Features de Hostelería (10 campos - GRUPO PRINCIPAL)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `n_bares_202206` | int | Número de bares en Feb 2022 (baseline) |
| `n_bares_202606` | int | Número de bares en Jun 2026 (actual) |
| `velocidad_crecimiento_anual` | float | % cambio anual promedio |
| `aceleracion_crecimiento` | float | Cambio en velocidad de crecimiento |
| `media_movil_12m` | float | Media móvil últimos 12 meses |
| `tendencia_54m` | float | Slope de regresión lineal 54 meses |
| `variabilidad_bares` | float | Desviación estándar del crecimiento |
| `cambio_acumulado_pct` | float | % cambio total Feb 2022 - Jun 2026 |
| `diversidad_categorias` | int | Número de categorías hosteleras diferentes |
| `bares_por_1000hab` | float | Densidad de bares per capita |

#### Features Demográficas (8 campos)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `poblacion_total` | int | Población total del barrio (2026) |
| `crecimiento_poblacion_anual` | float | % cambio anual población |
| `edad_media` | float | Edad promedio de residentes |
| `pct_extranjeros` | float | % de población extranjera |
| `densidad_poblacional` | float | Habitantes por km² |
| `tasa_natalidad` | float | Nacimientos por 1000 hab |
| `indice_diversidad_cultural` | float | Shannon index de nacionalidades |
| `pct_menores_30` | float | % de población < 30 años |

#### Features Económicas (6 campos)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `renta_media_2023` | float | Renta media anual (€) |
| `renta_mediana_2023` | float | Renta mediana anual (€) |
| `cambio_renta_2015_2023` | float | % cambio renta en 8 años |
| `categoria_renta` | str | Quintil: muy-baja/baja/media/alta/muy-alta |
| `desigualdad_gini` | float | Coeficiente Gini de desigualdad |
| `pct_poblacion_renta_baja` | float | % población en quintil más bajo |

#### Features Geográficas (3 campos)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `distancia_centro_km` | float | Distancia a Plaza Mayor (km) |
| `proximidad_estaciones_metro` | int | Número estaciones metro en 500m |
| `zona` | str | Categoría: Centro/Norte/Sur/Este/Oeste |

#### Variable Target (Obligatorio)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `gentrificara` | int | VARIABLE OBJETIVO: 1=SÍ, 0=NO (etiquetado manual) |

**Total de campos:** 32 (2 ID + 30 features + 1 target)

**Clave primaria:** `barrio_id` (única por barrio)

**Variables de especial relevancia:**
- `gentrificara` (target para clasificación)
- `velocidad_crecimiento_anual` (feature más importante esperada)
- `cambio_acumulado_pct` (fuertemente correlacionado con target)
- `renta_media_2023` (diferencia entre barrios gentrificados vs no)

**Fases posteriores que la consumirán:**
1.**EDA exploratorio:** Análisis univariante, bivariante, correlaciones
2. **Modelado ML:** Train/test split, entrenamiento Logistic/SVM/XGBoost
3. **Evaluación:** Métricas, validación cruzada, SHAP values
4. **Visualización:** Mapa interactivo, feature importance, dashboard
5. **Presentación:** Ranking TOP 10, predicciones finales

### Datasets Secundarios de Gold (ACTUALIZADO)

#### `gold_barrios_predicciones.csv`
- **Descripción:** Tabla de predicciones finales (128 barrios × predicción + confianza)
- **Granularidad:** Una fila por barrio
- **Campos:** barrio_id, barrio_nombre, prediccion_si_no, probabilidad, top_3_features
- **Uso:** Ranking interactivo, dashboard, informe ejecutivo

#### `gold_validacion_registradores.csv` ⭐ NUEVA (PRIMARIA)
- **Descripción:** Validación rigurosa: predicción ML vs precio oficial Registradores
- **Granularidad:** Barrio (1:1 con gold_barrios_completo)
- **Campos:** barrio_id, barrio_nombre, probabilidad_ml, precio_m2_registradores, validacion_status
- **Validación lógica:** Barrios predichos "SÍ" deben tener precios ALTOS o estar en escalera de riesgo
- **Uso:** ⭐ Validación principal del target + análisis de confiabilidad
- **Ventaja:** Granularidad BARRIO (vs DISTRITO anterior), fuente oficial

#### `gold_validacion_idealista.csv` (SECUNDARIA)
- **Descripción:** Correlación entre predicción ML y cambio de precios Idealista
- **Granularidad:** Distrito (21 zonas)
- **Campos:** distrito, prediccion_promedio, cambio_precio_observado, correlacion
- **Uso:** Validación complementaria (si Registradores insuficiente)
- **Nota:** Utilidad secundaria, mantener para redundancia

---

## 5. Relaciones Entre Datos

### Estructura Relacional (ACTUALIZADA)

```
CENSO_LOCALES (raw)
    ↓ (agregación por barrio × mes)
FEATURES_HOSTELERIA (processed)
    ↓ (merge por barrio)
┌──────────────────────────────┐
│  GOLD_BARRIOS_COMPLETO       │ ← TABLA CENTRAL
│  (128 barrios × 32 columnas) │
└──────────────────────────────┘
    ↑ (left join)   ↑ (left join)   ↑ (left join)      ↑ (inner join) ⭐
    │               │               │                   │
PADRÓN          RENTA (INE)    PRECIOS_IDEALISTA   REGISTRADORES/TINSA
(1:1)           (1:1)          (1:N barrio→dist)   (1:1 - PRIMARIO)

┌──────────────────────────────┐
│  GOLD_VALIDACION_REGISTRADORES
│  Predicción ML vs Precio Official
│  (154 barrios × 5 columnas) ⭐ NEW
└──────────────────────────────┘
```

**Cambio crítico:** Registradores/TINSA se integra como **validación primaria** (inner join = 1:1)

### Detalles de Relaciones

**1. Censo Locales → Features Hostelería**
- Relación: N:1 (muchos locales → 1 barrio)
- Clave: `barrio_id` (en censo locales)
- Agregación: COUNT(locales), SUM(cambios), etc por mes
- Tipo: Serie temporal mensual (54 meses)

**2. Features Hostelería → Gold Barrios**
- Relación: 1:1 (1 fila feature = 1 fila gold)
- Clave: `barrio_id`
- Transformación: Resumen 54 meses → 1 fila (velocidad, aceleración, etc)
- Tipo: LEFT JOIN (todo barrio tiene features)

**3. Padrón → Gold Barrios**
- Relación: 1:1 (1 snapshot padrón por barrio)
- Clave: `barrio_id` (agregación sección censal → barrio)
- Tipo: LEFT JOIN
- Problema potencial: Padrón es snapshot (jul 2026), no serie temporal

**4. Renta (INE) → Gold Barrios**
- Relación: 1:1 (renta 2023 por barrio)
- Clave: `barrio_id` (agregación sección censal → barrio)
- Tipo: LEFT JOIN
- Problema potencial: Renta es de 2023 (3 años atrás)

**5. Registradores/TINSA → Gold Validación (⭐ PRIMARIA - NUEVA)**
- Relación: 1:1 (1 barrio = 1 registro de precio)
- Clave: `barrio_id` (mapeo directo de barrio_nombre)
- Granularidad: 154 barrios individuales (máxima precisión)
- Tipo: INNER JOIN (solo barrios con precio registral)
- Ventaja: Oficialidad + granularidad (vs Idealista que es por distrito)
- Uso: ⭐ Validación rigurosa del target + análisis de correlación
- **Output:** `gold_validacion_registradores.csv` (nueva métrica de confiabilidad)

**6. Precios Idealista → Gold Validación (SECUNDARIA)**
- Relación: 1:N (1 barrio → potencialmente múltiples distritos)
- Clave: `barrio_id` → `distrito_id` (lookup table)
- Tipo: LEFT JOIN (opcional, para validación complementaria)
- Limitación: Precios a nivel distrito, features a nivel barrio
- Uso: Validación secundaria si Registradores insuficiente

### Posibles Problemas al Cruzar

1. **Cambios de clasificación de barrios:** El Ayuntamiento podría haber reclasificado barrios entre 2022-2026
   - Solución: Usar código oficial de barrio (barrio_id) como fuente de verdad única

2. **Falta de datos en padrón:** Si un barrio no existe en padrón, no habrá features demográficas
   - Solución: COALESCE con valores promedio del distrito

3. **Agregación de sección censal → barrio:** Hay ~500 secciones censales en Madrid, debo mapearlas a 128 barrios
   - Solución: Usar tabla de correspondencia oficial de INE

4. **Desalineación temporal:** Censo locales es mensual, renta es anual, padrón es snapshot
   - Solución: Usar datos al cierre de mes (última observación conocida)

---

## 6. Diccionario de Datos Inicial

### Diccionario Completo de Capa Gold

| Campo | Tipo | Fuente | Obligatorio | Rango/Categorías | Observaciones |
|-------|------|--------|------------|-----------------|---|
| `barrio_id` | int | Ayto Madrid | Sí | 1-128 | Código único oficial |
| `barrio_nombre` | str | Ayto Madrid | Sí | Malasaña, Chueca, etc | Nombre oficial |
| `n_bares_202202` | int | Censo Locales | Sí | 0-300+ | Conteo snapshot Feb 2022 |
| `n_bares_202606` | int | Censo Locales | Sí | 0-300+ | Conteo snapshot Jun 2026 |
| `velocidad_crecimiento_anual` | float | Derivado | Sí | -50% a +200% | % cambio anual promedio |
| `aceleracion_crecimiento` | float | Derivado | Sí | -10% a +50% | Cambio en velocidad (delta de delta) |
| `media_movil_12m` | float | Derivado | Sí | 0-300+ | Promedio últimos 12 meses |
| `tendencia_54m` | float | Derivado | Sí | -5 a +10 | Slope de regresión lineal |
| `variabilidad_bares` | float | Derivado | Sí | 0-100 | Desviación estándar mensual |
| `cambio_acumulado_pct` | float | Derivado | Sí | -50% a +400% | % cambio total 54 meses |
| `diversidad_categorias` | int | Censo Locales | Sí | 1-20 | Número de categorías diferentes |
| `bares_por_1000hab` | float | Derivado | Sí | 0-100 | Densidad per capita |
| `poblacion_total` | int | Padrón Municipal | Sí | 5000-80000 | Habitantes 2026 |
| `crecimiento_poblacion_anual` | float | Derivado | Approx | -5% a +15% | Basado en snapshot único |
| `edad_media` | float | Padrón Municipal | Sí | 30-50 años | Promedio barrio |
| `pct_extranjeros` | float | Padrón Municipal | Sí | 5%-50% | Proporción % |
| `densidad_poblacional` | float | Derivado | Sí | 100-12000 hab/km² | Población ÷ área |
| `tasa_natalidad` | float | Padrón Municipal | Approx | 5-20 por 1000 | Estimado si no disponible |
| `indice_diversidad_cultural` | float | Derivado | Sí | 0-5 (Shannon) | Mayor = más diverso |
| `pct_menores_30` | float | Padrón Municipal | Sí | 20%-50% | % población joven |
| `renta_media_2023` | float | INE | Sí | €15000-€50000 | Anual |
| `renta_mediana_2023` | float | INE | Sí | €15000-€50000 | Anual |
| `cambio_renta_2015_2023` | float | INE | Sí | -20% a +50% | Variación 8 años |
| `categoria_renta` | str | Derivado | Sí | muy-baja, baja, media, alta, muy-alta | Quintiles |
| `desigualdad_gini` | float | Derivado | Sí | 0-1 | Mayor = más desigual |
| `pct_poblacion_renta_baja` | float | INE | Sí | 10%-40% | Quintil inferior |
| `distancia_centro_km` | float | Geométrico | Sí | 0-20 km | Plaza Mayor como referencia |
| `proximidad_estaciones_metro` | int | Límites Barrios | Sí | 0-10 | Estaciones en 500m |
| `zona` | str | Geométrico | Sí | Centro, Norte, Sur, Este, Oeste | Categoría geográfica |
| `gentrificara` | int | ETIQUETADO MANUAL | Sí | 0 o 1 | TARGET VARIABLE |

---

## 7. Problemas de Calidad Esperados

### Específicos de Mi Proyecto

#### 1. **Cambios en Clasificación de Epigrafe** 
**Problema:** El Ayuntamiento cambió la clasificación de "tipo de actividad" (epigrafe) entre 2022-2026
- Ej: "BAR" → "BARES Y CAFETERÍAS"
- **Impacto:** Conteo de "bares" puede ser inconsistente entre años
- **Detección:** Habrá saltos abruptos en categorías específicas
- **Solución:** Normalizar descripciones a términos estándar antes de contar

#### 2. **~10% de Registros sin Descripción de Epigrafe** 
**Problema:** 39,206 locales en el dataset no tienen descripción de actividad
- **Impacto:** No puedo identificarlos como hostelería o no
- **Solución:** Excluir del conteo de hostelería (conservador), o usar categoría por omisión

#### 3. **Padrón es Snapshot, no Serie Temporal** 
**Problema:** Solo tengo padrón de julio 2026, no puedo medir CAMBIO en población
- **Impacto:** Feature `crecimiento_poblacion_anual` será estimado, no observado
- **Solución:** Usar proyecciones INE o asumir cambio lento (no es feature crítica)

#### 3b. **Registradores/TINSA - Mapeo de Barrios** ⭐ NUEVO
**Problema:** El archivo tiene 154 registros, pero algunos barrios pueden estar duplicados o tener nombres ligeramente diferentes
- **Ej:** "Pacifico" vs "Pacífico", "Lucero" (Usera) vs "Lucero" (otro distrito)
- **Impacto:** Merge por `barrio_nombre` podría fallar si hay mismatch
- **Detección:** Verificar que todos los 128 barrios principales tengan match
- **Solución:** Usar fuzzy matching (similitud de texto) + validación manual
- **Confiabilidad:** ✅ Alta (datos oficiales del Colegio de Registradores)

#### 4. **Renta tiene 3 Años de Antigüedad** 
**Problema:** Datos de renta son de 2023, puede haber cambiado
- **Impacto:** Feature de renta puede no reflejar realidad 2026
- **Solución:** Asumir que ranking de barrios (pobre vs rico) es estable

#### 5. **Precios Solo a Nivel Distrito, no Barrio** 
**Problema:** Precios Idealista agregados por 21 distritos, features a nivel 128 barrios
- **Impacto:** No puedo validar predicción a nivel barrio individual
- **Solución:** Agrupar predicciones por distrito y comparar con precios distritales

#### 6. **Desbalance de Clases en Target** 
**Problema:** Probablemente habrá más barrios SIN gentrificación (~85%) que CON (~15%)
- **Impacto:** Modelo puede sesgarse hacia predicción mayoritaria
- **Solución:** SMOTE o class_weight en XGBoost

#### 7. **Poco Histórico de Precios (12 meses)** 
**Problema:** Solo puedo validar con 12 meses de datos de precios
- **Impacto:** Validación será limitada
- **Solución:** Usar como validación cualitativa, no cuantitativa

#### 8. **Potencial Falta de Datos en Barrios Periféricos** 
**Problema:** Algunos barrios pequeños pueden tener pocos locales registrados
- **Impacto:** Features derivadas pueden ser ruidosas
- **Solución:** Aplicar suavizado (media móvil) a series con pocos datos

#### 9. **Duplicados en Censo Locales** 
**Problema:** Mismo local puede aparecer múltiples veces si cambió de estado
- **Impacto:** Conteo será inflado
- **Solución:** Usar fecha más reciente de cada local único

#### 10. **Cambios de Geometría de Barrios** 
**Problema:** Límites de barrios podrían haber cambiado
- **Impacto:** Mappeo de sección censal → barrio puede ser incorrecto
- **Solución:** Verificar con tabla oficial de correspondencia del INE

---

## 8. Decisiones de Limpieza y Transformación Previstas

### Fase 1: Raw → Processed (Consolidación y Limpieza)

#### Tratamiento de Valores Nulos

| Problema | Ubicación | Acción | Justificación |
|----------|-----------|--------|---|
| **NaNs en descripción epigrafe** | Censo Locales (39k registros) | Excluir del conteo hostelería | Conservative: no asumo categoría |
| **NaNs en edad media padrón** | Padrón Municipal | Imputar con edad promedio barrio | Pocas excepciones esperadas |
| **NaNs en renta mediana** | Renta INE | Imputar con renta media barrio | Correlación esperada alta |
| **NaNs en proximidad metro** | Derivado de geometría | Usar 0 (muy alejado) | Barrios sin metro cercano = periféricos |

#### Tratamiento de Duplicados

- **Censo Locales:** Un local puede tener múltiples registros si cambió estado
  - Acción: Usar `barrio_id + codigo_local` como clave única
  - Conservar: Último registro por fecha

- **Padrón y Renta:** Sin duplicados esperados (datos oficiales)

#### Normalización de Fechas

- **Formato:** YYYY-MM-DD en todos los datasets
- **Valores fuera de rango:** Rechazar cualquier fecha < 2014-01 o > 2026-12

#### Normalización de Categorías

- **Epigrafe (tipo de actividad):** Mapear a lista estándar
  - BARES, CAFETERÍAS, RESTAURANTES → `BAR`
  - PIZZERÍAS, COMIDA RÁPIDA → `RESTAURANTE`
  - etc

- **Zona:** Asignar automáticamente por coordenadas vs geometría
  - Valores: Centro, Norte, Sur, Este, Oeste

#### Mapeo de Registradores → Gold Barrios ⭐ NUEVO

| Problema | Ubicación | Acción | Justificación |
|----------|-----------|--------|---|
| **Nombres inconsistentes** | Registradores vs Censo Locales | Fuzzy matching + validación | 154 vs 128 barrios |
| **Barrios duplicados** | Registradores (Pacífico, Lucero) | Deduplicar por distrito + nombre | Evitar merge incorrecto |
| **Barrios faltantes** | Si algunos de 128 no tienen precio | Inner join (solo con match) | Será 128 o 128- depende |
| **Precios extremos** | Barrios céntricos muy caros | Mantener (información real) | Gentrificación es sobre precios |

#### Tratamiento de Outliers

- **Densidad de bares:** Cap en P99 (limitar valores extremos de barrios céntricos)
- **Renta:** No remover (desigualdad es información real)
- **Población:** No remover (barrios grandes son válidos)
- **Precios Registradores:** No remover (son datos reales, no estimaciones)

---

## 9. Riesgos del Modelo de Datos

### ¿Qué parte está más CLARA?

**Hostelería (Censo Locales):** 54 meses de datos oficiales, bien estructurados, comprensible cómo contar bares

**Límites geográficos:** Barrios son entidades estables, geometrías públicas disponibles

**Target binario:** Barrios como Malasaña/Chueca ya gentrificaron (historia conocida)

### ¿Qué genera más INCERTIDUMBRE?

**Padrón sin histórico:** Solo snapshot 2026, crecimiento poblacional es estimado

**Renta antigua (2023):** Cambios recientes no visibles, asumo estabilidad

**Precios Registradores:** ✅ RESUELTO - Tengo 154 barrios con precios oficiales, no estimados

**Definición de gentrificación:** Concepto complejo, pero ahora validable con Registradores (precios reales)

### ¿Qué fuente PUEDE DAR MÁS PROBLEMAS?

**Censo Locales (CRITICIDAD: ALTA)**
- Problema: ~10% sin descripción, cambios de clasificación
- Impacto: Features principales son derivadas de esto
- Mitigación: QA riguroso en semana 1, detectar anomalías

**Etiquetado manual (CRITICIDAD: BAJA)** ✅ MEJORADO
- Antes: Solo 4-5 barrios etiquetados, resto incierto
- Ahora: ✅ Validable con Registradores (154 barrios con precios reales)
- Impacto: Desbalance 85:15 sigue presente pero validable
- Mitigación: SMOTE + class_weight en modelo + validación con Registradores

**Mapping sección censal → barrio (CRITICIDAD: MEDIA)**
- Problema: 500 secciones → 128 barrios, puede haber excepciones
- Impacto: Features demográficas pueden estar en barrio incorrecto
- Mitigación: Usar tabla oficial de INE + validación cruzada

**Mapeo Registradores → Gold (CRITICIDAD: BAJA)**
- Problema: 154 barrios en Registradores, 128 en Censo Locales
- Nombres inconsistentes (ej. "Pacifico" vs "Pacífico")
- Mitigación: Fuzzy matching + validación manual

### ¿Qué ocurriría si NO PUEDO construir la capa gold tal como definida?

**Escenario 1:** Padrón no tiene datos para un barrio
- **Contingencia:** Usar valores promedio del distrito o ciudad
- **Riesgo:** BAJO (pocos barrios sin padrón)

**Escenario 2:** Etiquetado resulta imposible (no hay consenso sobre qué es gentrificación)
- **Contingencia:** ✅ Usar Registradores como target (precios reales > umbral = gentrificado)
- **Riesgo:** ✅ BAJO RESUELTO (Registradores proporciona target natural)

**Escenario 3:** Cambios en clasificación de epigrafe impiden contar bares consistentemente
- **Contingencia:** Usar google places API como fuente alternativa
- **Riesgo:** BAJO (detectaré en semana 1)

### ¿Qué ALTERNATIVA para simplificar si fuera necesario?

Si la capa gold es demasiado compleja:

**Plan B Simplificado:**
1. Reducir features: Solo 10 (cantidad bares, cambio bares, renta, población, edad, extranjeros)
2. Eliminar features geográficas: No es crítico para clasificación
3. Usar menos barrios: Entrenar solo en 50 barrios principales
4. Etiquetado binario simple: Solo 2 categorías (céntrico=gentrificado, periférico=no)

**Impacto:** F1-Score bajaría a ~0.70, pero modelo seguiría siendo viable

**Realismo:** Creo que lograré la capa gold completa (estimado 98% confianza) ⭐ MEJORADO

---

## 10. CONCLUSIÓN - MODELO DE DATOS ✅ ROBUSTO

### Mejoras Críticas con Registradores/TINSA

**Antes de Registradores:**
- ❌ Validación por distrito (21 zonas)
- ❌ Precios de portal (estimaciones, no reales)
- ❌ Target sin validación rigurosa

**Después de Registradores:**
- ✅ Validación por barrio (154 barrios, 1:1)
- ✅ Precios oficiales (Colegio de Registradores)
- ✅ Target validable con datos reales
- ✅ Output: `gold_validacion_registradores.csv` (nueva métrica)

### Confianza en Construcción de Capa Gold

**Antes:** 95%  
**Después:** 98% ⭐ MEJORADO

**Razones de la mejora:**
- Registradores resuelve el problema de granularidad
- Validación ahora es rigurosa, no teórica
- No hay punto de fallo crítico sin alternativa

---

*Documento actualizado: 2026-09-21*  
*Mejora principal: Integración Registradores/TINSA*
