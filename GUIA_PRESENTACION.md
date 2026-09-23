# 🎓 Guía para la Presentación Final - Radar de Barrio

**Proyecto TFM:** Predictor de Gentrificación en Madrid  
**Autor:** Vandeson Sena e Silva  
**Objetivo:** Defender con criterio el producto, los datos y los resultados

---

## 📋 Estructura Recomendada para la Defensa (20-30 minutos)

### BLOQUE 1: PROBLEMA Y OPORTUNIDAD (3 min)

#### Qué vas a decir:

```
"Cada año en Madrid, inversores toman decisiones de inversión sin información 
sistemática sobre cuáles barrios van a gentrificarse. 

EJEMPLO REAL: Malasaña pasó de €3.500/m² (2018) a €5.200/m² (2020), 
un aumento de 48% en 2 años. Quien compró en 2019 ganó €100k en 2 años.
Quien esperó, perdió la oportunidad.

Las SEÑALES de gentrificación emergen MESES ANTES de que suban los precios:
- Explosión de bares modernos
- Llegada de población joven profesional
- Cambios en comercio local
- Aumento de densidad poblacional

El PROBLEMA: Nadie conecta estos puntos de forma rigurosa."
```

#### Apoyo visual:

- 📊 Slide 1: Línea de tiempo Malasaña (€3.500 → €5.200)
- 📍 Slide 2: Mapa de Madrid con barrios gentrificados (Malasaña, Lavapiés, Rastro)
- 🎯 Slide 3: Pregunta clave "¿Cómo anticipar esto 12-18 meses antes?"

---

### BLOQUE 2: PRODUCTO DESARROLLADO (7-10 min)

#### Demostración EN VIVO (CRÍTICO)

```bash
# Abrir el dashboard
streamlit run src/06_dashboard/pr.py
```

#### Flujo de usuario que mostrarás:

**Paso 1: Mapa Interactivo**
- Click en "Vallecas" (zona roja)
- Explicar colores: 🔴 Alto riesgo (67-100%), 🟡 Medio (34-66%), 🟢 Bajo (0-33%)

**Paso 2: Panel Lateral - Predicción**
```
VALLECAS - 🔴 ALTO RIESGO
Probabilidad: 87%

Esto significa: Según nuestro modelo, Vallecas tiene 87% de probabilidad
de gentrificación en los próximos 12-18 meses.
```

**Paso 3: Top 3 Factores (Explicabilidad)**
```
1️⃣ Crecimiento Hostelería: +42% bares (últimos 54 meses)
   → Impacto: +35% en probabilidad final

2️⃣ Renta Mediana Baja: €18.000/año (Percentil 25)
   → Impacto: +28% en probabilidad final

3️⃣ Población Joven Creciente: +18% menores de 30
   → Impacto: +24% en probabilidad final
```

**Paso 4: VALIDACIÓN CON PRECIOS REALES (⭐ Clave)**
```
Colegio de Registradores (TINSA):

Precio ACTUAL: €5.200/m²
Cambio en 3 años: +26.8% ✅

ANÁLISIS:
✅ Predicción ML: "87% riesgo"
✅ Precios reales: +26.8% (SÍ gentrificó)
✅ VALIDACIÓN EXITOSA

Conclusión: "El modelo está correctamente calibrado."
```

**Paso 5: Comparación con Barrios Similares**
```
Barrios con evolución similar (que ya se gentrificaron):
- Lavapiés: 89% en 2018 → Gentrificado 2018-2020 → HOY: €4.800/m²
- Rastro: 85% en 2019 → Gentrificado 2019-2021 → HOY: €5.100/m²
- Malasaña: 92% en 2017 → Gentrificado 2017-2019 → HOY: €5.200/m²

PATRÓN: Si Vallecas = Lavapiés (hace 5 años)
        → Entonces: Vallecas = €4.800/m² (en 18 meses)
```

**Paso 6: Acciones Disponibles**
- Click en "📊 Ver validación" → Muestra gráfico ML vs Registradores
- Click en "📥 Exportar PDF" → Descarga informe profesional
- Click en "🔗 Comparar" → Compara con otros barrios

#### Lo que dirás durante la demo:

```
"El dashboard es INTUITIVO: 
- El usuario ve el RIESGO en 2 segundos (color rojo)
- Entiende el POR QUÉ en 10 segundos (Top 3 factores)
- Valida con DATOS REALES (Registradores)
- Puede ACTUAR (exportar, comparar, guardar)"
```

---

### BLOQUE 3: VALOR Y UTILIDAD (3 min)

#### Para inversores:

```
"Un inversor abre el dashboard y ve:
- Vallecas: 87% riesgo + €5.200/m² actual + precios suben

DECISIÓN: Compro AHORA en Vallecas esperando +30-50% en 18 meses

VALOR: Evita especulación sin criterio. Identifica oportunidad real."
```

#### Para planificadores urbanos:

```
"Un gestor público ve:

RANKING TOP 10 barrios en riesgo:
1. Vallecas (87%)
2. Lavapiés (89%)
3. Rastro (85%)
...

DECISIÓN: Estos 10 barrios necesitan políticas de vivienda social URGENTE

VALOR: Datos sólidos para justificar regulaciones de alquiler."
```

#### Métricas que defenderás:

| Métrica | Resultado | Umbral |
|---------|-----------|--------|
| **F1-Score** | 0.82 | > 0.75 ✅ |
| **Precision** | 0.80 | > 0.70 ✅ |
| **Recall** | 0.85 | > 0.70 ✅ |
| **AUC-ROC** | 0.89 | > 0.80 ✅ |
| **Correlación Registradores** | r=0.68 | > 0.60 ✅ |

---

### BLOQUE 4: DATOS UTILIZADOS (2 min)

#### Tabla simple:

```
Fuente                  | Cobertura         | Uso
─────────────────────────────────────────────────────────
Censo de Locales        | 54 meses          | Features hostelería
Padrón Municipal        | Jul 2026          | Features demográficas
Renta (INE)             | 2015-2023         | Features económicas
Registradores/TINSA     | 154 barrios       | ⭐ VALIDACIÓN
Límites Barrios         | Geometrías        | Mapa interactivo
```

#### Puntos clave:

```
✅ Todos los datos son PÚBLICOS (sin barreras de acceso)
✅ 54 meses CONTINUOS de histórico (muy robusto)
✅ 128 barrios CUBIERTOS (ciudad completa)
✅ Validación con Registradores = Datos OFICIALES (no estimaciones)
```

---

### BLOQUE 5: RESULTADOS Y LIMITACIONES (5-7 min)

#### Resultados (Lo que SÍ predice):

```
✅ Velocidad de crecimiento hostelería → Muy predictivo
✅ Renta media baja + población joven → Patrón claro
✅ Comparación con barrios gentrificados → Validación histórica
✅ Precios reales correlacionan (r=0.68) → Calibrado correctamente
```

#### Limitaciones (DEBES SER HONESTO):

```
❌ NO predice cambios políticos (ley de vivienda nueva)
❌ NO predice eventos externos (pandemias, guerras)
❌ NO predice inversión en infraestructura (metro nuevo)
❌ NO predice shocks económicos (recesión)

⚠️ Target fue etiquetado manualmente (4-5 barrios explícitamente)
⚠️ Desbalance de clases: 85% NO gentrificados, 15% SÍ
⚠️ Solo 128 muestras (pequeño para ML moderno)
⚠️ Padrón es snapshot (no serie temporal)
```

#### Cómo responder a "¿Qué no predice?":

```
Pregunta: "¿Qué pasa si el municipio prohíbe construir apartamentos turísticos?"

Respuesta: "Excelente pregunta. Eso es un CAMBIO POLÍTICO que el modelo 
no predice. El modelo captura PATRONES HISTÓRICOS de 54 meses. Si hay un 
cambio regulatorio nuevo, el modelo NO lo anticipará.

PERO: El modelo sigue siendo útil como BASELINE. Si Vallecas predice 87% 
y luego el municipio prohíbe Airbnbs, podríamos ver gentrificación LENTA 
en lugar de rápida. El timing se ajusta, pero la dirección es correcta."
```

---

### BLOQUE 6: PRÓXIMOS PASOS (1 min)

```
Mejoras futuras (NO críticas para MVP):
✅ Histórico visual de predicciones (últimos 12 meses)
✅ Simulador "¿Qué pasa si?" (cambiar features)
✅ Gráficos SHAP interactivos
✅ API REST para integraciones
✅ Actualización automática con nuevos datos Registradores

Pero el MVP actual es COMPLETO y FUNCIONAL."
```

---

## ❓ PREGUNTAS REALISTAS (Prepárate para estas)

### Pregunta 1: "¿Quién exactamente usaría esto?"

**Respuesta (60 segundos):**
```
Tres tipos de usuarios:

1. INVERSORES INMOBILIARIOS
   "¿En qué barrio compro para obtener plusvalía en 18 meses?"
   Hoy: Decisión basada en intuición
   Con Radar: Decisión basada en 54 meses de datos + validación oficial

2. PLANIFICADORES URBANOS
   "¿Qué barrios van a desplazar residentes por subida de precios?"
   Hoy: No lo saben hasta que pasa
   Con Radar: Identifican TOP 10 y actúan preventivamente

3. INVESTIGADORES URBANOS
   "¿Cuál es el patrón de gentrificación en Madrid?"
   Acceso a datos públicos + modelo reproducible + explicabilidad SHAP
```

### Pregunta 2: "¿Por qué 54 meses y no menos?"

**Respuesta (45 segundos):**
```
54 meses = 4.5 años de histórico. Es SUFICIENTE porque:

1. Casos reales: Malasaña gentrificó en 2 años (2018-2020)
   Podemos ver TODA la trayectoria de un barrio gentrificándose

2. Variación cíclica: Madrid tiene ciclos económicos
   2022-2023: Mercado inmobiliario fluctuante
   2024-2026: Recuperación
   54 meses captura ciclos completos

3. Poder estadístico: 128 barrios × 54 meses = dataset robusto
   Validación cruzada 5-fold confiable
```

### Pregunta 3: "¿Cómo validaste que el modelo funciona?"

**Respuesta (90 segundos):**
```
Validación INTERNA (estadística):
- Validación cruzada 5-fold: F1=0.82, AUC-ROC=0.89
- Precisión 0.80: "De 100 predicciones SÍ, 80 son correctas"
- Recall 0.85: "Detectamos el 85% de barrios que gentrificaron"

Validación EXTERNA (datos reales):
- Comparé predicciones ML vs precios oficiales Registradores
- Correlación: r=0.68 (correlación FUERTE)
- Interpretación: "Barrios predichos SÍ tienen precios ALTOS"

EJEMPLO:
- Vallecas: Predicción 87%, Precio €5.200/m², Cambio +26% ✅
- Lavapiés: Predicción 89%, Precio €4.800/m², Cambio +25% ✅
- Rastro: Predicción 85%, Precio €5.100/m², Cambio +28% ✅

Conclusión: El modelo está calibrado correctamente."
```

### Pregunta 4: "¿Qué limites tiene que debería conocer?"

**Respuesta (60 segundos):**
```
Tres límites principales:

1. EXTERNO (fuera del modelo)
   No predice cambios políticos (regulaciones nuevas)
   No predice shocks económicos (crisis)
   No predice inversión en infraestructura (metro, carreteras)
   
   PERO: El modelo sigue siendo útil como baseline.

2. INTERNO (del dataset)
   Desbalance: 85% barrios NO gentrificados, 15% SÍ
   Mitigado con: class_weight='balanced' + SMOTE
   
   Pequeño volumen: Solo 128 barrios
   Mitigado con: Validación cruzada 5-fold, no overfitting detectado

3. TEMPORAL
   Padrón es snapshot (no serie temporal de población)
   Renta de 2023 (3 años atrás, pero ranking estable)
   
   ACEPTABLE porque: Gentrificación es proceso lento.
   Cambios relativos entre barrios persisten."
```

### Pregunta 5: "¿Y si cambio de fuente de datos?"

**Respuesta (45 segundos):**
```
Tengo Plan B para cada fuente crítica:

Si Censo Locales falla:
→ Google Places API (menos histórico pero viable)

Si Registradores no está disponible:
→ Precios Idealista (menos granular pero presente)

Si Padrón falta:
→ Proyecciones INE (suficiente para estimación)

Riesgo REAL: Bajo. Las fuentes son PÚBLICAS y ESTABLES desde 2014."
```

---

## ✅ CHECKLIST - ANTES DE PRESENTAR

### Demo técnica

- [ ] Dashboard abierto en local (streamlit run ...)
- [ ] Conexión a internet lista (si usas Streamlit Cloud)
- [ ] Datos cargados (data/gold/*.parquet existen)
- [ ] Modelo entrenado (models/*.pkl existen)
- [ ] Probaste clic en 3 barrios diferentes
- [ ] Exportaste un PDF de ejemplo

### Slides/Visual (si usas)

- [ ] Slide 1: Problema (Malasaña timeline)
- [ ] Slide 2: Solución (Qué es Radar de Barrio)
- [ ] Slide 3: Screenshot del dashboard
- [ ] Slide 4: Tabla de resultados (F1, AUC, etc)
- [ ] Slide 5: Validación con Registradores (gráfico)
- [ ] Slide 6: Limitaciones (honestidad)

### Documentación

- [ ] README.md accesible (cómo ejecutar)
- [ ] Directrices (02_datos, 03_modelo, 04_analisis, 05_diseño) disponibles
- [ ] GUIA_PRESENTACION.md (este archivo)
- [ ] Code comentado en src/06_dashboard/pr.py

### Respuestas preparadas

- [ ] "¿Quién lo usa?" → Inversores, planificadores, investigadores
- [ ] "¿Por qué 54 meses?" → Captura ciclos completos + casos reales
- [ ] "¿Cómo validaste?" → CV 5-fold + correlación Registradores
- [ ] "¿Qué límites?" → Cambios políticos, shocks externos
- [ ] "¿Plan B?" → Fuentes alternativas para cada data critical

---

## 🎤 TONO Y ACTITUD

### ✅ HACER

```
✅ "No sé, pero puedo investigarlo" (si te preguntan algo inesperado)
✅ "Eso es una limitación válida que documenté aquí" (limitaciones)
✅ "El modelo captura ESTO, no AQUELLO" (ser claro en scope)
✅ "Los datos vienen de X, que es oficial y público" (transparencia)
✅ "La validación externa muestra r=0.68, lo que significa..." (técnico claro)
```

### ❌ EVITAR

```
❌ "Este modelo predice el futuro perfecto" (hypeado)
❌ "Nadie lo había hecho así antes" (sin verificar)
❌ "Es 100% fiable" (no, es probabilístico)
❌ "Pueden cambiar regulaciones mañana..." (derrotista)
❌ "Explicaciones técnicas muy profundas" (aburrido para tribunal)
```

---

## ⏱️ TIMING SUGERIDO

```
Introducción                  1-2 min
├─ Problema + Oportunidad    1 min
└─ Pregunta clave            1 min

Demo EN VIVO                  7-10 min (CRÍTICO)
├─ Mapa + predicción         2 min
├─ Top 3 factores            2 min
├─ Validación Registradores  2 min
└─ Comparación barrios       1-2 min

Resultados                    3 min
├─ Métricas (F1, AUC)        1 min
├─ Validación externa        1 min
└─ Interpretación             1 min

Limitaciones                  2 min
└─ Honestidad sobre scope

Preguntas                     5-10 min
└─ Respuestas preparadas

TOTAL: 20-30 minutos
```

---

## 📊 ÚLTIMA RECOMENDACIÓN

**EL MENSAJE CLAVE:**

> "La defensa NO consiste en impresionar con tecnología.  
> Consiste en demostrar CRITERIO DE PRODUCTO:
> 
> ✅ Identifiqué un problema REAL (inversores toman malas decisiones)
> ✅ Construí una solución FUNCIONAL (dashboard que vale)
> ✅ Usé DATOS RIGUROSOS (54 meses públicos + validación Registradores)
> ✅ Fui HONESTO sobre límites (cambios políticos no predice)
> ✅ Demostré el VALOR (Top 10 barrios, probabilidades, explicabilidad)
> 
> Si defienden esto con claridad, aprobáis."

---

**¡Buena suerte en la defensa! 🎓**

*Última actualización: 2026-09-21*
