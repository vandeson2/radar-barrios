# Entrega 4 - Diseño del Análisis y Estrategia de Modelado

**Proyecto:** Predictor de Gentrificación - Clasificador ML  
**Estudiante:** Vandeson Sena e Silva 

---

## 1. Problema que se Busca Resolver

### Problema Actual

Cada año en Madrid, **inversores, compradores y planificadores urbanos toman decisiones de inversión sin información sistemática sobre cuáles barrios están en proceso de transformación urbana**. Las señales de gentrificación emergen meses antes de que se reflejen en precios (explosión de bares modernos, llegada de población joven profesional, cambios en comercio), pero **nadie conecta estos puntos de forma rigurosa**.

Ejemplo real: Malasaña pasó de €3,500/m² (2018) a €5,200/m² (2020), un aumento de 48%. Los que compraron en 2019 ganaron; los que esperaron demasiado, perdieron la oportunidad.

### Quién Utiliza el Resultado y Para Qué Decisión

**Usuarios principales:**
1. **Inversores inmobiliarios:** ¿En qué barrio comprar para obtener plusvalía en 12-24 meses?
2. **Planificadores urbanos:** ¿Qué barrios necesitan políticas de vivienda para evitar desplazamiento?
3. **Comerciantes:** ¿Dónde abrir un negocio que atraiga clientela nueva?
4. **Residentes:** ¿Qué barrio será más caro/seguro/dinámico en el futuro?

**Decisión que mejora:** En lugar de confiar en intuición o datos parciales, decidir basándose en un modelo ML que identifica patrones históricos.

### Qué Resultado Se Considera Útil

El proyecto debería producir:

**Un clasificador** que prediga para CADA barrio de Madrid: **¿Gentrificará en los próximos 12 meses? SÍ/NO**

**Con confianza explícita:** Probabilidad asociada (ej: "Vallecas gentrificará con 87% de confianza")

**Explicable:** Top 3 features que motivan cada predicción (ej: "+48% bares nuevos, +12% población joven, renta baja")

**Actionable:** Ranking TOP 10 de barrios en riesgo inmediato de gentrificación

**Integrable:** Dashboard interactivo, mapa de Madrid coloreado, informe ejecutivo

---

## 2. Análisis de Datos Planteado y Utilidad Esperada

### Preguntas Clave a Responder

#### Grupo A: Evolución de Hostelería (La pregunta central)

1. **¿Cuál es la velocidad de crecimiento de hostelería por barrio?**
   - ¿Hay barrios con explosión reciente de bares/cafés?
   - ¿Qué barrios crecen más rápido que la media?
   - ¿Existe aceleración (el crecimiento se está acelerando)?

2. **¿Hay diferencia entre barrios gentrificados vs no gentrificados en hostelería?**
   - Hipótesis: Malasaña/Chueca (gentrificados) mostraron +40% bares antes de explotar precios
   - Vallecas (no gentrificado) ha tenido cambios mínimos (<10% bares)

3. **¿Qué tipo de hostelería crece? (Categorización)**
   - ¿Crece "hostelería moderna" (cafeterías hipster, restaurantes) o todo?
   - Hipótesis: Gentrificación se asocia con diversificación de categorías

#### Grupo B: Contexto Demográfico

4. **¿Qué barrios tienen población joven y profesional?**
   - Hipótesis: Gentrificación atrae población <35 años
   - ¿Correlación entre % menores de 30 y crecimiento hostelería?

5. **¿Qué barrios tienen baja renta actual?**
   - Hipótesis: Gentrificación ocurre en barrios de baja renta (mercado sin explotar)
   - Barrios ricos ya están gentrificados

6. **¿Hay relación entre diversidad cultural y gentrificación?**
   - ¿Barrios con alta diversidad son más "atractivos" para nueva población?

#### Grupo C: Relaciones entre Variables

7. **¿Qué variables mejor predicen gentrificación?**
   - Esperado: Velocidad de bares >> edad media >> renta
   - SHAP values mostrarán importancia real

8. **¿Hay multicolinealidad o redundancia en features?**
   - Ej: ¿"Población total" y "Densidad" dicen lo mismo?

### Análisis Específicos Planteados

#### FASE 1: EDA Exploratorio

**Análisis Univariante:**
- Distribución de velocidad de crecimiento de bares 
- Distribución de renta por barrio
- Distribución de población 
- Detección de outliers en cada variable

**Análisis Bivariante:**
- Scatter: Velocidad bares vs Cambio renta 
- Scatter: % Extranjeros vs Velocidad bares
- Scatter: Edad media vs Crecimiento hostelería

**Análisis Temporal:**
- Evolución mensual de bares en TOP 5 barrios vs bottom 5 barrios
- Visualizar aceleración: ¿el crecimiento está acelerado o estable?
- Detección de cambios abruptos 

**Análisis Geográfico:**
- Mapa de Madrid coloreado por velocidad de crecimiento
- ¿Hay clustering geográfico? 

**Segmentación:**
- Agrupar barrios en 3 clusters: Alto crecimiento (riesgo), Medio, Bajo
- Caracterizar cada cluster 

#### FASE 2: Análisis Pre-Modelado 

**Correlación con Target:**
- Tabla de correlaciones: cada feature vs `gentrificara` (0/1)
- Visualizar con heatmap
- Identificar features más predictivas

**Balance de Clases:**
- Contar: ¿Cuántos barrios gentrificados vs no?
- Esperado: 85% NO, 15% SÍ (desbalance)
- Estrategia: SMOTE o class_weight

**Feature Importance Preliminar:**
- Random Forest rápido para ranking de features
- Descartar features débiles

#### FASE 3: Post-Modelado

**Análisis de Errores:**
- Falsos positivos: Barrios que dije "gentrificará" pero no
  - ¿Qué características anómalas tienen?
  - ¿Están en transformación pero más lenta?

- Falsos negativos: Barrios que dije "NO" pero sí gentrificaron
  - ¿Qué nos perdimos?
  - ¿Hay un patrón alternativo?

**Validación Post-Hoc:**
- Comparar predicciones con cambio REAL de precios (12 meses observados)
- ¿Barrios predichos "SÍ" realmente subieron precios?

### Hipótesis Principales a Comprobar

| Hipótesis | Valor para MVP | Cómo se valida |
|-----------|----------------|---|
| **H1:** Velocidad de crecimiento hostelería predice gentrificación | Alta | Correlación + Feature Importance |
| **H2:** Barrios de baja renta + alta hostelería = gentrificación | Alta | Scatter 2D + Análisis cluster |
| **H3:** Población joven atrae hostelería moderna | Media | Correlación, no core para ML |
| **H4:** Densidad poblacional no afecta gentrificación | Baja | Excluir feature si correlación <0.1 |
| **H5:** Diversidad cultural es factor secundario | Baja | Usar pero esperar Feature Importance bajo |

### Visuales y Indicadores para MVP

- **Mapa de Madrid:** Barrios coloreados (Verde=SÍ, Amarillo=Posible, Rojo=NO)
- **Feature Importance:** Top 10 gráfico horizontal
- **SHAP Values:** Force plot explicando predicción de Vallecas/Malasaña
- **Timeseries:** Evolución de bares en TOP 3 barrios
- **Scatter:** Velocidad vs Renta (coloreado por predicción)
- **ROC Curve:** Comparación de 3 modelos
- **Matriz Confusión:** Errores del mejor modelo
- **TOP 10 Ranking:** Tabla interactiva (barrio, probabilidad, features clave)

---

## 3. Tipo de Modelos que se van a Plantear

### Tipo de Problema: Clasificación Binaria Supervisada

Predecir si cada barrio de Madrid gentrificará en próximos 12 meses (SÍ=1, NO=0)

**Por qué clasificación y no regresión:**
- Tengo 54 meses de features de hostelería (robusto para clasificación)
- Solo 12 meses de precios (insuficiente para regresión)
- Pregunta binaria es más útil que "precio exacto"
- Métricas de clasificación (F1, Precision, Recall) son estándares

### Modelo Baseline: Logistic Regression

| Aspecto | Descripción |
|--------|------------|
| **¿Por qué?** | Sencillo, interpretable, fast baseline |
| **Ventajas** | Fácil de explicar (coeficientes = importancia), rápido de entrenar, probabilidades calibradas |
| **Limitaciones** | Asume relaciones lineales; puede perder patrones complejos |
| **Utilidad** | Si SVM/XGBoost no superan esto, significa features son débiles |

### Modelo Candidato 1: SVM (Support Vector Machine) con Kernel RBF

| Aspecto | Descripción |
|--------|------------|
| **¿Por qué?** | Captura relaciones no lineales mejor que Logistic; buen balance entre complejidad e interpretabilidad |
| **Ventajas** | Maneja bien espacios de alta dimensión (30 features); robusto a outliers |
| **Limitaciones** | Menos interpretable que Logistic; más lento; requiere escalado (StandardScaler) |
| **Cuándo usar** | Si hay patrones no lineales en datos |


### Modelo Candidato 2: XGBoost Classifier (Estado del Arte)

| Aspecto | Descripción |
|--------|------------|
| **¿Por qué?** | Mejor rendimiento esperado en clasificación tabular; feature importance built-in; maneja desbalance bien |
| **Ventajas** | Alta precisión; feature importance (top 10); probabilidades bien calibradas; SHAP compatible |
| **Limitaciones** | Menos interpretable que Logistic; riesgo de overfitting; más lento que SVM |
| **Cuándo usar** | Cuando precisión es crítica |


### Tabla Comparativa de Modelos

| Alternativa | Tipo | Por qué se plantea | Limitación principal | Métrica esperada |
|---|---|---|---|---|
| **Baseline** | Logistic Regression | Referencia sencilla, interpretable | Puede perder patrones complejos | F1 ~0.65 |
| **Candidato 1** | SVM (RBF) | Captura no-linealidad; balance interpretabilidad-complejidad | Menos interpretable; más lento | F1 ~0.78 |
| **Candidato 2** | XGBoost | Estado del arte en tabular; feature importance; SHAP | Riesgo overfitting; menos interpretable | F1 ~0.82 |

---

## 4. Datos de Entrada del Análisis y los Modelos

### Dataset Principal: `gold_barrios_completo.parquet`

**Nombre:** `gold_barrios_completo.parquet`  
**Granularidad:** Una fila por barrio (128 filas totales)  
**Fecha de referencia:** Junio 2026 (cierre de datos)  
**Clave primaria:** `barrio_id` (1-128)

### Variables de Entrada - Matriz Completa

#### ✅ Variables UTILIZADAS en Modelo ML

| Grupo | Variable | Tipo | Rango | Uso | Transformación |
|-------|----------|------|-------|-----|---|
| **Hostelería** | velocidad_crecimiento_anual | float | -50% a +200% | Feature principal | Normalizar (StandardScaler) |
| | aceleracion_crecimiento | float | -10% a +50% | Feature principal | Normalizar |
| | cambio_acumulado_pct | float | -50% a +400% | Feature principal | Normalizar |
| | media_movil_12m | float | 0-300+ | Feature de contexto | Normalizar |
| | tendencia_54m | float | -5 a +10 | Feature de suavizado | Normalizar |
| | variabilidad_bares | float | 0-100 | Mide volatilidad | Normalizar |
| | diversidad_categorias | int | 1-20 | Mide sofisticación | Log transform |
| | bares_por_1000hab | float | 0-100 | Densidad per capita | Normalizar |
| | n_bares_202606 | int | 0-300+ | Tamaño absoluto | Log transform |
| **Demográfica** | poblacion_total | int | 5k-80k | Feature de contexto | Log transform |
| | edad_media | float | 30-50 años | Feature de contexto | Normalizar |
| | pct_extranjeros | float | 5%-50% | Diversidad | Normalizar |
| | pct_menores_30 | float | 20%-50% | Población joven | Normalizar |
| | densidad_poblacional | float | 100-12000 | Tamaño | Log transform |
| **Económica** | renta_media_2023 | float | €15k-€50k | Feature clave | Log transform |
| | categoria_renta | str | muy-baja...muy-alta | One-hot encoding | 5 variables binarias |
| | cambio_renta_2015_2023 | float | -20% a +50% | Tendencia | Normalizar |
| | desigualdad_gini | float | 0-1 | Mide desigualdad | Normalizar |
| **Geográfica** | zona | str | Centro/N/S/E/O | Contexto espacial | One-hot encoding (5 vars) |
| | distancia_centro_km | float | 0-20 km | Centralidad | Normalizar |
| | proximidad_estaciones_metro | int | 0-10 | Accesibilidad | Normalizar |

---

## 5. Datos de Salida y Forma de Consumo

### Variable Objetivo: `gentrificara` (Target)

| Atributo | Valor |
|----------|-------|
| **Tipo** | Binaria (0 / 1) |
| **Significado** | 1 = Barrio gentrificará en próximos 12 meses; 0 = NO |
| **Granularidad** | Por barrio (128 valores únicos) |
| **Fuente de verdad** | Etiquetado manual validado con histórico (Malasaña, Chueca, etc = 1) |

### Salida Principal: Predicción + Probabilidad

| Campo | Descripción | Tipo |
|-------|------------|------|
| `barrio_id` | Identificador único | int |
| `barrio_nombre` | Nombre del barrio | str |
| `prediccion` | SÍ gentrificará o NO | int |
| `probabilidad` | Confianza de predicción (0-1) | float |
| `nivel_riesgo` | Categoría visual | str |
| `feature_top1` | Razón principal | str |
| `feature_top2` | Razón secundaria | str |
| `feature_top3` | Razón terciaria | str |

### Salida Secundaria: Ranking y Detalle

#### `gold_barrios_predicciones.csv`

Tabla con ranking de barrios por probabilidad de gentrificación:

**Uso posterior:**
- Dashboard interactivo: Mostrar TOP 10
- Informe ejecutivo: Barrios en riesgo inmediato
- Mapa: Codificar color por probabilidad

#### `gold_analisis_errores.csv`

Para validación post-hoc.

### Formato de Entrega - MVP

| Formato | Componente | Uso |
|---------|-----------|-----|
| **CSV** | gold_barrios_predicciones.csv | Ranking, tabla interactiva |
| **Parquet** | gold_analisis_completo.parquet | Almacenamiento eficiente, análisis |
| **Pickle** | xgboost_model.pkl | Servir predicciones en producción |
| **HTML** | mapa_madrid_predicciones.html | Visualización interactiva |
| **Dashboard** | streamlit_app.py | MVP principal (Streamlit) |
| **JSON** | predicciones_api.json | API para integración |

### Cómo Usa el Usuario la Salida

**Escenario 1: Investor**
1. Abre dashboard
2. Ve mapa de Madrid coloreado
3. Hace click en "Vallecas" (verde = gentrificará)
4. Ve: "87% de probabilidad, razones: +48% bares nuevos, +12% población joven"
5. **Decisión:** Compra vivienda en Vallecas esperando plusvalía

**Escenario 2: Urban Planner**
1. Descarga ranking TOP 10
2. Ve que Vallecas, Carabanchel, Villaverde gentrificarán
3. Identifica: "Estos barrios necesitan políticas de vivienda social urgente"
4. **Decisión:** Propone regulación de alquileres en estos barrios

**Escenario 3: Dashboard Explorador**
1. Usuario navega mapa, filtra por zona
2. Selecciona "Rango de renta" para ver "barrios pobres con potencial"
3. Compara predicciones con precios observados
4. **Decisión:** Valida hipótesis con datos visuales

---

## 6. Estrategia de Validación y Evaluación

### Separación de Datos

**Train / Test Split:**
- 80% entrenamiento (103 barrios)
- 20% prueba (25 barrios)
- Estratificado por target (mantiene 85-15 ratio)
- Random state: 42 (reproducibilidad)

**Por qué estratificado y no aleatorio:**
Con solo 128 muestras y 15% de clase positiva, aleatorio podría dar test con 0 positivos. Estratificado garantiza representación.

### Validación Cruzada (K-Fold)

```python
StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
```

- **5 folds** porque n=128 es pequeño
- **Estratificado** para mantener 85-15 en cada fold
- **Shuffle=True** para evitar sesgos de orden

### Métricas de Evaluación Seleccionadas

| Métrica | Fórmula | Por qué es apropiada | Interpretación |
|---------|---------|---|---|
| **F1-Score** | 2×(Prec×Rec)/(Prec+Rec) | Balancea precision y recall; importante en desbalance | 0.85 = 85% balance entre falsos positivos y negativos |
| **Precision** | TP/(TP+FP) | Mide "de los que dije SÍ, cuántos acerté" | 0.82 = 82% de predicciones "gentrificará" son correctas |
| **Recall** | TP/(TP+FN) | Mide "de los SÍ reales, cuántos detecté" | 0.88 = detectamos 88% de barrios que gentrificaron |
| **AUC-ROC** | Área bajo curva ROC | Mide discriminación a todos los thresholds | 0.89 = modelo muy bueno |
| **Matriz Confusión** | TP, FP, FN, TN | Visualiza errores específicos | Ver qué tipo de error predomina |




### Criterios de Aceptación

| Criterio | Umbral | Acción si falla |
|----------|--------|---|
| **F1-Score** | > 0.75 | Revisar features débiles; considerar SMOTE |
| **Precision** | > 0.70 | Aumentar threshold de probabilidad |
| **Recall** | > 0.70 | Reducir threshold; aceptar más falsos positivos |
| **Estabilidad CV** | Std < 0.05 | Aumentar n_splits; revisar regularización |
| **No overfitting** | Train-Test < 0.05 | Aplicar regularización; reducir complejidad |
| **Generalización** | Validar con precios reales | Si no correlaciona, replantear definición de target |


---

## 8. Riesgos y Alternativas

### Riesgo 1: ¿Variable Target Está Disponible y es Válida?

**Problema:** El target `gentrificara` lo etiqueto manualmente (Malasaña=1, Vallecas=0)
- ¿Qué pasa si mi definición es incorrecta?
- ¿Qué si hay barrios "en el límite" (medio gentrificados)?

**Severidad:** ALTA (afecta todo el modelo)

**Mitigación:**
- Validar etiquetas con cambio REAL de precios (si tengo 12 meses de datos)
- Hacer prueba de correlación: barrios etiquetados "1" deben tener +precios
- Si correlación < 0.5, replantear target

**Plan B si falla:**
- Usar regresión en lugar de clasificación (predecir % cambio de precios)
- O usar clustering automático (K-means) para etiquetar sin supervisión

---

### Riesgo 2: ¿Data Leakage o Información Futura?

**Problema:** ¿Estoy usando información que NO estaría disponible en momento de predicción real?

**Análisis:**
- Velocidad bares: Disponible (datos históricos 54 meses) 
- Renta 2023: Disponible (datos publicados) 
- Padrón 2026: Disponible (publicado) 
- Precios 2025-2026: Disponible (datos públicos) 
- Cambio FUTURO de precios: NO, eso es lo que queremos predecir 

**Conclusión:** Sin data leakage detectado

---

### Riesgo 3: ¿Volumen y Calidad Suficientes?

| Aspecto | Valor | ¿Suficiente? |
|--------|-------|---|
| **Muestras (barrios)** | 128 | Bajo pero aceptable para clasificación |
| **Ratio positivos/negativos** | 85/15 | Desbalance alto, manejable con class_weight |
| **Features** | 30 | Razonable (ratio 4:1 muestras:features) |
| **Histórico hostelería** | 54 meses | Excelente |
| **Histórico precios** | 12 meses | Limitado, solo para validación |

**Conclusión:** Suficiente, pero margen estrecho. Requiere validación rigurosa.

---

### Riesgo 4: ¿Desbalance Extremo de Clases?

**Problema:** 85% NO gentrificará, 15% SÍ
- Modelo puede sesgarse a predecir mayoría "NO"
- Recall de clase positiva puede ser bajo

**Mitigación:**
1.  `class_weight='balanced'` en Logistic + SVM
2. `scale_pos_weight=5` en XGBoost (peso 5:1)
3. SMOTE si no es suficiente
4. Usar **F1 como métrica principal** (no Accuracy)


---

### Riesgo 5: ¿Cambios Temporales o Sesgos de Cobertura?

**Problema:** 
- El Ayuntamiento cambió clasificación de epigrafe entre 2022-2026
- Censo locales puede tener cobertura variable (menos datos en 2022?)

**Mitigación:**
- EDA: Graficar número de locales por mes, detectar discontinuidades
- Si hay cambio abrupto, investigar causa
- Posible: Usar solo últimos 24 meses de datos "consistentes"

---

### Riesgo 6: ¿Features Débiles o Redundantes?

**Problema:**
- Feature Importance revela que "cambio_acumulado_pct" y "velocidad_anual" son idénticas
- O que "poblacion_total" es ruido

**Mitigación:**
- Analizar correlación matrix antes de modelar
- Usar selección de features: eliminar si correlación > 0.9 entre features
- O usar regularización (L1 en Logistic penaliza coeficientes pequeños)

**Plan B:** Reducir a top 15 features más predictivas

---

### Riesgo 7: ¿Modelo No Supera Baseline?

**Problema:** XGBoost F1 = 0.69 (similar a Logistic 0.68)

**Plan B:**
1. Revisar feature engineering (¿features realmente predictivas?)
2. Aumentar histórico (usar datos más antiguos si disponibles)
3. Usar ensemble (promedio de 3 modelos)
4. Replantear target (¿definición de gentrificación es correcta?)
5. O simplemente admitir: "Gentrificación es compleja, modelo moderado es útil"

---

### Riesgo 8: ¿Validación Post-Hoc Falla?

**Problema:** Predice "barrio SÍ gentrificará" pero precios no suben

**Mitigación:**
- No es fallo fatal (solo 12 meses de datos de precios = validación limitada)
- Análisis: ¿El barrio está gentrificando pero más lentamente?
- Interpretar como: "Señales correctas, timing diferente"

---

### Síntesis de Riesgos

| Riesgo | Severidad | Probabilidad | Mitigación | Plan B |
|--------|-----------|--------------|-----------|--------|
| Target inválido | ALTA | MEDIA | Validar con precios | Regresión |
| Data leakage | ALTA | BAJA | Revisar variables | Ninguno |
| Desbalance clases | MEDIA | ALTA | class_weight + F1 | SMOTE |
| Features débiles | MEDIA | MEDIA | EDA + correlación | Reducir features |
| Modelo no mejora baseline | MEDIA | MEDIA | Revisar features | Ensemble |
| Validación falla | BAJA | BAJA | Aumentar histórico | Aceptar validación cualitativa |

**Confianza General:** 85% de que proyecto será exitoso con modelo F1 > 0.75

---

## Conclusión

La estrategia es clara, realista y viable:

**Problema:** Inversores necesitan saber qué barrios gentrificarán  
**Análisis:** EDA + preguntas concretas sobre hostelería, demografía, renta  
**Modelos:** Baseline (Logistic) + 2 candidatos (SVM, XGBoost)  
**Validación:** Train/test 80-20 + 5-fold CV + F1 como métrica  
**Salida:** Predicción binaria + probabilidad + TOP 10 ranking + visuales  
**Riesgos:** Identificados y mitigados  

