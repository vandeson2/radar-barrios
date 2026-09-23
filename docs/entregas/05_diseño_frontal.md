# Entrega 5 - Diseño del Frontal y Experiencia de Usuario

**Proyecto:** Predictor de Gentrificación - Clasificador ML  
**Estudiante:** Vandeson Sena e Silva  

---


## 1. Resumen de la Solución y del Usuario

### Problema que Resuelve

**Cada año en Madrid, inversores toman decisiones de compra/inversión sin información sistemática sobre cuáles barrios van a gentrificarse.**

Las señales de gentrificación emergen MESES ANTES de que se reflejen en precios:
-  Explosión de bares/restaurantes modernos
-  Llegada de población joven profesional
-  Cambios acelerados en comercio local
-  Aumento de densidad poblacional

Pero nadie las conecta de forma rigurosa.

**Ejemplo real - CASO MALASAÑA:**
```
Año 2018: €3,500/m²
Año 2020: €5,200/m² (+48% en 2 años)

Inversores que compraron 2019: GANARON 
Inversores que esperaron 2021: PERDIERON OPORTUNIDAD
```

**La pregunta crítica:** ¿Cómo anticipar estos movimientos 12-18 meses antes?

### Usuario Principal: Inversor Inmobiliario

| Atributo | Descripción |
|----------|-------------|
| **Perfil** | Persona física/empresa que toma decisiones de inversión en Madrid |
| **Motivación** | Maximizar rentabilidad identificando barrios antes de gentrificación |
| **Contexto de uso** | Evaluación de oportunidades de compra (5-10 min de análisis rápido) |
| **Nivel técnico** | Medio (entiende datos, no necesariamente ML) |
| **Problema que enfrenta** | "¿Vale la pena invertir en Vallecas ahora? ¿Se gentrificará en 2 años?" |

### Usuario Secundario: Planificador Público / Gestor Municipal

| Atributo | Descripción |
|----------|-------------|
| **Perfil** | Municipalidad, gestoría pública de vivienda, investigador urbano |
| **Motivación** | Identificar barrios que necesitan política de vivienda/preservación |
| **Contexto de uso** | Planificación estratégica, argumentación política (15-30 min análisis) |
| **Nivel técnico** | Bajo a medio |
| **Problema que enfrenta** | "¿Qué barrios vamos a perder? ¿Dónde invertir en vivienda social?" |

### Tarea Principal del Usuario

**Usuario Inversor:**
```
"Quiero saber en 5 minutos si un barrio gentrificará.
Necesito:
1. Respuesta clara (SÍ/NO) con probabilidad
2. Razones principales (Top 3 factores)
3. Comparación con barrios similares
4. Historial de cómo cambió el riesgo (últimos meses)
5. Exportar informe para presentar a inversores"
```

**Usuario Gestor Público:**
```
"Quiero entender el riesgo de gentrificación en TODOS los barrios.
Necesito:
1. Ranking de barrios por riesgo
2. Identificar dónde intervenir urgentemente
3. Datos sólidos para justificar políticas
4. Visualización espacial (mapa) para presentar a concejales"
```

### Tipo de Producto

**Dashboard Predictivo + Mapa Interactivo**

```
COMPONENTES:
├─ Clasificador SVM (RBF) entrenado
├─ Predicción binaria (SÍ/NO gentrificación)
├─ Probabilidad asociada (0-100%)
├─ Top 3 factores explicados (SHAP)
├─ Mapa interactivo de Madrid
├─ Tabla ranking por riesgo
└─ Exportación de informe PDF
```

### Resultado Principal para el Usuario

```
Para cada barrio de Madrid:

┌─────────────────────────────────────┐
│ BARRIO: Vallecas                    │
│                                     │
│ PREDICCIÓN: ✓ ALTO RIESGO           │
│ Probabilidad: 87%                   │
│                                     │
│ RAZONES PRINCIPALES:                │
│ 1. Crecimiento hostelería: +42%     │
│ 2. Renta mediana baja (P25)         │
│ 3. Población joven creciente: +18%  │
│                                     │
│ Barrios similares:                  │
│ • Lavapiés (actualmente 89% riesgo) │
│ • Rastro (actualmente 85% riesgo)   │
│                                     │
│ [Exportar PDF] [Ver detalle] [Comparar]│
└─────────────────────────────────────┘
```

---

## 2. Imagen Mockup del Frontal

![Mockup del Frontal - Radar de Barrio](assets/05_mockup_frontal.png)

**Nota:** Diseño profesional 1920×1200px con:
- Mapa interactivo (izquierda 50%)
- Panel lateral con predicción (derecha 40%)
- Tabla ranking (abajo 10%)

---

## 3. Justificación del Diseño

### 3.1. Utilidad y Valor de la Solución

#### Problema Resuelto: De Intuición a Datos

```
ANTES:
Inversor: "Me gusta Vallecas, parece que se mueve..."
Resultado: Decisión basada en intuición, pierde oportunidades

DESPUÉS:
Inversor: Consulta Radar de Barrio
Resultado: "87% de riesgo, +42% hostelería, renta baja"
Decisión: COMPRO AHORA (datos sólidos)
Impacto: +€100k de rentabilidad en 2 años
```

#### Información Esencial vs. Secundaria

**Mostrar en pantalla principal (5-10 segundos):**
- Nombre barrio
- 🔴 ALTO RIESGO / 🟡 MEDIO / 🟢 BAJO (visual clear)
- Probabilidad exacta (87%)
- Top 3 factores con impacto (bullets cortos)
- Barrios comparables (contexto)

**Mostrar en panel de detalles (opcional):**
- Gráficos SHAP dependence plots
- Evolución histórica (últimos 12 meses)
- Todos los 30 features ordenados
- Métricas de validación del modelo

**NUNCA mostrar:**
- Parámetros técnicos SVM (kernel, C, gamma)
- 30 features listados sin contexto
- Matriz de confusión o AUC-ROC
- Código del modelo

#### Conversión: Predicción → Decisión → Acción

```
CAPA TÉCNICA (invisible):
30 features de hostelería, demografía, economía
    ↓ [SVM RBF + SHAP]
Predicción: 87% gentrificación + Top 3 factores

         ↓ [TRADUCCIÓN A NEGOCIO]

CAPA DE USUARIO (lo que VE):
"Vallecas: ALTO RIESGO (87%)"
"Porque: Hostelería +42%, Renta baja, Población joven"
"Barrios similares: Lavapiés (gentrificado 2018-2020)"

         ↓ [EMPODERAMIENTO]

CAPA DE ACCIÓN (lo que HACE):
"Estos datos justifican compra AHORA en Vallecas"
"Espero 12-18 meses → Vendo +30-50%"
[Descarga informe PDF para financiera]
```

---

### 3.2. Flujo de Usuario - 6 Pasos

#### PASO 1: Punto de Entrada (0-5 segundos)

Usuario accede a: `app.streamlit.com/radar-barrio`

**Qué VE:**
- Mapa interactivo de Madrid en grande (60% pantalla)
- 130 barrios coloreados por riesgo
- Tabla ranking sidebar (40% pantalla)
- Colores inmediatos: 🔴🟡🟢

**Lo que ENTIENDE:**
```
"Veo todos los barrios.
Rojo = Alto riesgo (gentrificación próxima)
Verde = Bajo riesgo (consolidado)
Puedo seleccionar uno y ver detalles."
```

#### PASO 2: Entrada de Usuario - Seleccionar Barrio (5-10 segundos)

**OPCIÓN A: Clic en mapa (intuitivo)**
```
Usuario: Click en Vallecas (zona roja)
Resultado: Panel lateral se abre con predicción 87%
```

**OPCIÓN B: Buscar en tabla (preciso)**
```
Usuario: Escribe "Vallecas" en buscador
Resultado: Tabla filtra, click en fila
```

**OPCIÓN C: Filtrar por riesgo (análisis rápido)**
```
Usuario: Checkbox "Solo rojo (alto riesgo)"
Resultado: Mapa/tabla se actualizan dinámicamente
Muestra: 32 barrios en riesgo máximo
```

#### PASO 3: Procesamiento (Invisible - ~1 segundo)

```
Backend (usuario no lo ve):
1. Carga 30 features de Vallecas
2. Normaliza con StandardScaler
3. Aplica modelo SVM RBF entrenado
4. Obtiene: predicción + probabilidad
5. Calcula SHAP values
6. Extrae Top 3 features
7. Busca barrios similares (clustering)
8. Prepara visualización
```

#### PASO 4: Resultado - Panel Lateral (10-15 segundos)

```
┌──────────────────────────────────────┐
│ 🏘️ VALLECAS                          │
│ ──────────────────────────────────── │
│                                      │
│ 🔴 ALTO RIESGO INMEDIATO             │
│ Probabilidad: 87%                    │
│                                      │
│ 📊 FACTORES QUE IMPULSAN:            │
│                                      │
│ 1️⃣ Crecimiento Hostelería           │
│    ↑ +42% bares (últimos 54 meses)   │
│    Impacto: +35%                     │
│                                      │
│ 2️⃣ Renta Mediana Baja               │
│    € €18.000/año (P25)               │
│    Impacto: +28%                     │
│                                      │
│ 3️⃣ Población Joven Creciente        │
│    ↑↑ +18% menores de 30             │
│    Impacto: +24%                     │
│                                      │
│ ──────────────────────────────────── │
│                                      │
│ 📍 CONTEXTO COMPARATIVO:             │
│ Percentil riesgo: P87 (Top 13%)      │
│                                      │
│ Barrios con evolución similar:       │
│ • Lavapiés (gentrificado 2018-2020)  │
│   Estaba aquí en 2018 = HOY SÍ       │
│                                      │
│ • Rastro (gentrificado 2019-2021)    │
│   Estaba aquí en 2019 = HOY SÍ       │
│                                      │
│ ──────────────────────────────────── │
│                                      │
│ 💡 ANÁLISIS HISTÓRICO:               │
│ Hace 12 meses: Medio riesgo (58%)    │
│ Hace 6 meses: Alto-medio (72%)       │
│ Hoy: Alto riesgo (87%)               │
│ Tendencia: ↑↑ ACELERADO              │
│                                      │
│ ──────────────────────────────────── │
│                                      │
│ 💰 VALIDACIÓN CON PRECIOS ⭐ NUEVO   │
│ Colegio de Registradores (TINSA)     │
│                                      │
│ Precio actual: €5.200/m²             │
│ Percentil: P82 (muy alto)            │
│ vs. hace 3 años: €4.100/m² (+26%)    │
│                                      │
│ Análisis: ✅ VALIDADO                │
│ Precios suben = Predicción correcta  │
│ Barrio está gentrificando            │
│                                      │
│ ⚠️ RECOMENDACIÓN:                    │
│ "Ventana se cierra PRONTO            │
│  Precios ya suben. Actuar YA"        │
│                                      │
│ ──────────────────────────────────── │
│ [📊 Ver análisis detallado]          │
│ [📊 Gráfico precios históricos]      │
│ [📥 Exportar informe PDF]            │
│ [🔗 Comparar con otros barrios]      │
│ [💾 Guardar para seguimiento]        │
└──────────────────────────────────────┘
```

#### PASO 5: Acciones - Lo que Usuario Puede Hacer

**A) Ver análisis detallado (2-5 min)**
```
Abre página secundaria con:
├─ Gráficos SHAP (relaciones causales)
├─ Timeseries: Cómo cambió riesgo últimos 12 meses
├─ Todos los 30 features (si quiere profundizar)
├─ Datos brutos normalizados
└─ Métricas de confianza del modelo
```

**B) Ver validación con precios reales ⭐ NUEVO**
```
Abre página secundaria con:
├─ Gráfico: Precio ML vs Registradores
├─ Scatter: Todos los 128-154 barrios
│  └─ Eje X: Predicción ML (%)
│  └─ Eje Y: Precio €/m² (Registradores)
│  └─ Bubble size: Tamaño del cambio
├─ Estadísticas: Correlación (r, ρ, p-value)
├─ Análisis por categoría (SÍ vs NO)
└─ Conclusión: "Modelo está validado ✅"

USO: Convencer a inversores que el modelo funciona
```

**C) Exportar informe profesional (1 click)**
```
PDF descargable con:
├─ Logo + Portada ejecutiva
├─ Resumen: "Vallecas = Alto riesgo (87%)"
├─ Top 3 factores explicados
├─ Validación: "Precios suben como predijo"
├─ Gráficos SHAP
├─ Comparación con barrios similares (con precios)
├─ Recomendación de acción
└─ Metodología técnica (QR a GitHub)

USO: Llevar a junta de inversores (MÁS CREÍBLE)
```

**C) Comparar múltiples barrios (análisis avanzado)**
```
Selecciona hasta 5 barrios:
├─ Vallecas (87%)
├─ Lavapiés (89%)
├─ Rastro (85%)
└─ Tabla comparativa:
   Barrio | Riesgo | Factor1 | Factor2 | Factor3
   ─────────────────────────────────────────────
   Vall. | 87% | +42% Host | Renta P25 | Joven +18%
   Lava. | 89% | +40% Host | Renta P20 | Joven +15%
```

**D) Guardar seguimiento (acceso futuro)**
```
"He guardado Vallecas.
Revísalo en 3 meses para ver evolución."

Mi lista:
• Vallecas (87%, guardado hace 5 días)
• Lavapiés (89%, guardado hace 2 sem)
• Rastro (85%, guardado hace 1 mes)
```

#### PASO 6: Excepciones y Errores

**Caso 1: Datos incompletos**
```
Usuario selecciona barrio sin datos de hostelería
   "Este barrio tiene datos INCOMPLETOS
   Falta: 6 meses de histórico hostelería
   
   Opciones:
   • Ver análisis parcial (con 24/30 features)
   • Reportar dato faltante [botón]"
```

**Caso 2: Confianza moderada**
```
Usuario selecciona barrio con predicción 55%
  "PREDICCIÓN MODERADA - Frontera de decisión
   Este barrio está ENTRE riesgo alto y medio.
   
   Razones: Factores contradictorios
   • Hostelería: ↑ (+12%, favorece)
   • Renta: → (estable, neutral)
   • Población: ↓ (-2%, desfavorece)
   
   Recomendación: Revisar en 3 meses"
```

**Caso 3: Barrio no encontrado**
```
Usuario busca "Salamanca" (typo: buscó "Salama")
"¿Quizás buscabas:
• Salamanca (187 resultados)
• Carabanchel Viejo (32 resultados)
• Carabanchel Alto (31 resultados)"
```

**Caso 4: Fallo técnico**
```
Backend demora >5 segundos
  "Analizando 30 features... 60%"

Si timeout:
  "Error al cargar. Reintentando...
   [Reintentar] [Volver al mapa]"
```

---

### 3.3. Experiencia de Usuario - Jerarquía Visual

#### Pirámide de Importancia

```
NIVEL 1: RESPUESTA VISUAL INMEDIATA (50% pantalla)
├─ Mapa interactivo de Madrid
├─ 130 barrios con colores 🔴🟡🟢
├─ Clic selecciona
└─ Usuario entiende RIESGO en 2 segundos

NIVEL 2: INFORMACIÓN CLAVE (35% pantalla)
├─ Panel lateral: "VALLECAS - 87% RIESGO"
├─ Top 3 Factores (bullets simples)
├─ Barrios comparables (contexto social)
└─ Usuario entiende POR QUÉ en 10 segundos

NIVEL 3: RANKING Y CONTEXTO (10% pantalla)
├─ Tabla: ranking de 130 barrios
├─ Filtros (por riesgo, zona, etc)
└─ Para análisis más profundo

NIVEL 4: ACCIONES AVANZADAS (5% pantalla)
├─ Botones: Detalles, Exportar, Comparar
├─ Para usuarios que quieren MÁS
└─ No interrumpe flujo principal
```

#### Simplicidad: Qué NO Mostrar

```
 EVITAR:
├─ 30 features técnicos listados
├─ Matriz de confusión o F1-score
├─ Parámetros SVM (kernel='rbf', C=1.0, gamma='scale')
├─ Código del modelo o SHAP fórmulas matemáticas
├─ Datos brutos normalizados (z-score)
└─ Métricas técnicas en pantalla principal

 HACER:
├─ "87% de riesgo" (simple, clara)
├─ "Porque: +Hostelería, +Población joven" (3 razones máximo)
├─ "Similar a Lavapiés que se gentrificó" (referencia real)
├─ Botón [Ver detalles técnicos] para expertos
└─ Lenguaje de usuario final (€/m², bares, jóvenes)
```

#### Legibilidad y Consistencia

**NOMBRES - Siempre iguales en todo:**
```
✓ "Crecimiento Hostelería" (nunca: "Bares aumentando")
✓ "Renta Mediana" (nunca: "Nivel económico")
✓ "Probabilidad: 87%" (nunca: "Confianza" o "Score")
✓ "Población Joven" (nunca: "Demografía")
```

**COLORES - Código consistente:**
```
🔴 Rojo = Alto riesgo (67-100%) → SÍ gentrificará
🟡 Amarillo = Medio riesgo (34-66%) → Posiblemente
🟢 Verde = Bajo riesgo (0-33%) → NO gentrificará

Aplicado en: Mapa, tabla, badges, gráficos, botones
```

**ICONOS - Claros:**
```
↑↑ = Factor favorable (rojo)
↓↓ = Factor desfavorable (verde)
→ = Factor neutral (gris)
```

---

## 4. Presentación de Resultados y Explicabilidad

### Resultado Principal

```
CLASIFICACIÓN BINARIA: SÍ / NO Gentrificación
MÉTRICA: Probabilidad (0-100%)

Ejemplo:
┌──────────────────────────────┐
│ VALLECAS                     │
│ 🔴 ALTO RIESGO               │
│ Probabilidad: 87%            │
│ → Gentrificará en 12-18 meses│
└──────────────────────────────┘
```

### Información Adicional

#### 1. Comparación - Ubicar en Contexto

```
Percentil de riesgo: P87 (Top 13% de barrios con MAYOR riesgo)

Distribución visual:
🟢 Bajo (0-33%): 98 barrios
🟡 Medio (34-66%): X barrios
🔴 Alto (67-100%): 32 barrios ← TÚ ESTÁS AQUÍ

Barrios con MISMO PERFIL histórico (gentrificados ya):
• Lavapiés: 89% en 2018 → Gentrificado 2018-2020 → HOY: €4.8k/m²
• Rastro: 85% en 2019 → Gentrificado 2019-2021 → HOY: €5.1k/m²
• Malasaña: 92% en 2017 → Gentrificado 2017-2019 → HOY: €5.2k/m²

PATRÓN: Si Vallecas = Lavapiés (hace 5 años)
        Entonces: Vallecas = €4.8k/m² (en 18 meses)
```

#### 1b. Validación - Precios Reales ⭐ NUEVO (REGISTRADORES)

```
VALIDACIÓN CON DATOS OFICIALES:
Colegio de Registradores / TINSA

Precio ACTUAL (Registradores):
€5.200/m² (Dato oficial, transacciones reales)

Precio 3 AÑOS ATRÁS:
€4.100/m² (estimado con tendencias)

Cambio observado: +26.8% ✅

ANÁLISIS DE CONFIANZA:
✅ Predicción ML: "87% riesgo" (barrio gentrificará)
✅ Precios reales: +26.8% en 3 años (SÍ gentrificó)
✅ VALIDACIÓN EXITOSA: Predicción = Realidad

BENEFICIO PARA USUARIO:
"El modelo está correctamente calibrado.
Vallecas es seguro para invertir AHORA."

[📊 Ver gráfico histórico de precios]
[📈 Comparar con otros barrios similares]
```

#### 2. Causas - Top 3 Factores (SHAP Explicable)

```
¿Por qué 87% de riesgo?

🥇 FACTOR PRINCIPAL: Crecimiento Hostelería
   ├─ Valor: +42% bares (últimos 54 meses)
   ├─ Interpretación: Explosión de oferta moderna
   └─ Impacto SHAP: +35% en probabilidad final

🥈 FACTOR SECUNDARIO: Renta Mediana Baja
   ├─ Valor: €18.000/año (Percentil 25)
   ├─ Interpretación: Barrio "sin explotar" = oportunidad
   └─ Impacto SHAP: +28% en probabilidad final

🥉 FACTOR TERCIARIO: Población Joven Creciente
   ├─ Valor: +18% menores de 30 (últimos 54 meses)
   ├─ Interpretación: Nueva demografía atrae hostelería
   └─ Impacto SHAP: +24% en probabilidad final

 Otros 27 factores: +13% combinado
   (demografía, geografía, etc. son secundarios)
```

#### 3. Incertidumbre - Ser Honesto

```
❌ NO DECIR (falso):
   "Vallecas SERÁ gentrificado al 100%"
   "Certeza del modelo: 87%"

✅ SÍ DECIR (correcto):
   "Según el modelo ML, Vallecas tiene 87% de probabilidad
    de gentrificación en próximos 12-18 meses, basado en
    patrones de barrios similares que ya se gentrificaron
    (Lavapiés 2018, Rastro 2019, Malasaña 2017)."

⚠️ CAVEATS SIEMPRE VISIBLES:
   • Modelo entrenado con 54 meses de datos
   • Datos actuales (hostelería) con 0 meses lag
   • No captura cambios políticos repentinos
   • Es probabilístico, no determinístico
```

#### 4. Histórico - Tendencia Temporal

```
Evolución de riesgo en VALLECAS:

Hace 12 meses: 🟡 Medio riesgo (58%)
└─ "Primeras señales de cambio"

Hace 6 meses: 🟡 Alto-Medio riesgo (72%)
└─ "Cambio acelerado"

HOY: 🔴 Alto riesgo (87%)
└─ "Punto de no retorno"

TENDENCIA: ↑↑ CRECIMIENTO ACELERADO

INTERPRETACIÓN:
"En 6 meses, riesgo subió 29 puntos (de 58% → 87%)
 Factor principal: +42% en hostelería
 
 VENTANA CRÍTICA: Próximos 6 meses
 Después: Precios ya habrán subido, oportunidad cerrada"
```

---

## 5. Alcance del MVP (Minimum Viable Product)

### ✅ FASE 1 - Implementado al Final del Curso

**BACKEND:**
```
✅ Cargar datos: data/gold/gold_barrios_completo_limpio.parquet
✅ Cargar modelo: outputs/ml/final_model/best_model_ensemble_v2.pkl
✅ Cargar SHAP: outputs/shap/feature_importance_shap.csv
✅ Cargar precios Registradores: Data/datos_precios_registradores_barrios.csv ⭐ NUEVO
✅ Predicción Ensemble para cada barrio
✅ Cálculo de SHAP Top 3 features
✅ Validación con precios reales (correlación ML vs Registradores)
✅ Identificar barrios similares (clustering)
```

**FRONTEND INTERACTIVO:**
```
 Mapa de Madrid interactivo (Folium)
   ├─ 130 barrios coloreados 🔴🟡🟢
   ├─ Click = abre panel lateral
   └─ Hover = muestra nombre + probabilidad

    Panel lateral informativo
   ├─ Nombre barrio + clasificación
   ├─ Probabilidad (grande, rojo)
   ├─ Top 3 Factores con impacto
   ├─ Validación con precios Registradores ⭐
   │  └─ "Precio actual: €X.XXX/m²"
   │  └─ "Cambio 3 años: +26%"
   ├─ Barrios similares (con precios)
   └─ 5 botones de acción

    Tabla ranking
   ├─ 130 barrios ordenados por riesgo
   ├─ Columnas: Rank | Barrio | % Riesgo | Factor Principal
   └─ Filtros (por riesgo, zona)

    Buscador
   ├─ Input texto "Vallecas"
   ├─ Filtro en tiempo real
   └─ Sugerencias si typo

   Exportador
   └─ Botón: Descargar PDF informe
```

**DATOS Y MODELOS:**
```
 130 barrios con predicciones (Ensemble: SVM + RF + GB)
 Probabilidades para cada barrio
 Top 3 features + impacto SHAP
 Precios reales Registradores (154 barrios) ⭐ VALIDACIÓN
 Validación: Correlación predicción vs precios
 Datos para comparación (barrios similares con precios)
```

**DOCUMENTACIÓN:**
```
 README del proyecto
 Guía de instalación (local + Streamlit Cloud)
 Guía de uso (usuario final)
 Limitaciones honestas del modelo
 Este documento (05_diseno_frontal.md)
```

**DEPLOYMENT:**
```
 Código en GitHub público
 Funciona en local: python -m streamlit run app.py
 Deployable en Streamlit Cloud (gratis)
 CI/CD básico opcional
```

---

## 6. CONCLUSIÓN - DISEÑO FRONTAL MEJORADO ⭐

### Impacto de Registradores en UX

**Antes:** Dashboard muestra predicciones sin validación  
**Ahora:** Dashboard muestra predicciones + validación con precios reales

| Aspecto | Antes | Después | Mejora |
|---------|-------|---------|--------|
| **Credibilidad** | "Modelo dice 87%" | "87% + precios suben +26%" | ✅ Prueba real |
| **Información** | Predicción binaria | Predicción + precio actual | ✅ Contexto |
| **Botones acción** | 4 | **5** | ✅ Ver validación |
| **Confianza usuario** | Media | Alta | ✅ Datos oficiales |

### Fortalezas del Diseño Final

✅ **Validación visual:** Precios Registradores en el panel lateral  
✅ **Comparación clara:** Barrios similares con precios históricos  
✅ **Nuevo botón:** "Ver validación" → Gráfico ML vs Registradores  
✅ **PDF mejorado:** Incluye datos de validación (más convincente)  
✅ **Transparencia:** Usuario ve que el modelo está calibrado correctamente

### Componentes MVP Finales

```
BACKEND:
✅ Predicción Ensemble (SVM + RF + GB)
✅ SHAP explicabilidad
✅ Precios Registradores (validación)
✅ Correlación ML vs precios reales

FRONTEND:
✅ Panel lateral con validación
✅ 5 botones de acción (incluye validación)
✅ Tabla ranking mejorada
✅ PDF con datos de validación

DATOS:
✅ 130 barrios predicciones
✅ 154 barrios precios Registradores
✅ Correlación y confianza del modelo
```

---

###  FASE 2 - Después del Curso (Opcional)

```
MEJORAS FUTURAS (No críticas para MVP):
├─ Gráficos SHAP interactivos (force plots, dependence)
├─ Simulador "¿Qué pasa si?" (modificar features)
├─ Histórico visual (12 meses atrás de predicciones)
├─ Gráfico de validación temporal (predicción vs precios)
├─ IA generativa (resumen narrativo auto)
├─ PDF exportable con logos + firma digital
├─ Autenticación (login de usuarios)
├─ Versión mobile responsive
├─ API REST para integraciones terceros
└─ Actualización automática con nuevos datos
```

*Documento actualizado: 2026-09-21*  
*Mejora principal: Integración Registradores/TINSA para validación visual*
