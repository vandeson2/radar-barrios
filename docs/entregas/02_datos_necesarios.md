# Entrega 2 - Análisis de Datos Necesarios (Machine Learning)

**Proyecto:** Predictor de Gentrificación - Clasificador ML   
**Estudiante:** Vandeson Sena e Silva


---

## 1. Idea Seleccionada: Clasificador de Gentrificación

He elegido desarrollar un clasificador de Machine Learning que prediga si un barrio de Madrid gentrificará en los próximos 12 meses. A continuación, desarrollo esta idea en tres párrafos:

### Problema que resuelve

Cada año en Madrid hay inversores, compradores y residentes que pierden dinero o se pierden oportunidades porque no ven venir la gentrificación de un barrio antes de que los precios exploten. Ejemplo real: Malasaña pasó de €3,500/m² (2018) a €5,200/m² (2020), un crecimiento de 48% que fue casi imposible de prever. El problema es que las señales de gentrificación están presentes meses antes de que se reflejen en precios (apertura acelerada de bares modernos, llegada de población joven, inversión en espacios públicos), pero nadie las conecta de manera sistemática. Mi proyecto resuelve esto permite a **inversores, planificadores urbanos y ciudadanos identificar cuáles barrios están en riesgo real de transformación** para poder tomar decisiones informadas antes de que sea demasiado tarde.

### Solución planteada

Mi enfoque es entrenar un **clasificador de Machine Learning supervisado** que prediga de forma binaria si un barrio gentrificará (SÍ/NO). El modelo tomará como entrada 54 meses históricos de evolución comercial (número de bares, cafeterías, restaurantes abiertos/cerrados por barrio), junto con contexto demográfico (población, edad media, renta media) para aprender patrones de gentrificación. La solución es superior a una regresión simple de precios porque primero, tengo 54 meses de datos comerciales pero solo 12 de precios (regresión fallaría por insuficiencia de datos), usar SÍ/NO es más interpretable y útil que predecir un precio exacto incierto, las métricas de clasificación (Precision, Recall, F1-Score) son estándares en ML y permiten validar rigorosamente. El resultado será un modelo entrenado con validación cruzada que pueda explicar mediante SHAP values exactamente por qué predice que un barrio gentrificará.

### MVP del proyecto final

Al finalizar el curso entregaré un paquete completo:
1. **Clasificador XGBoost** entrenado con validación cruzada (5-fold) y evaluado con métricas formales (Accuracy, Precision, Recall, F1-Score ≥0.75, AUC-ROC ≥0.80). 
2. **Dashboard interactivo en Streamlit** que permite seleccionar un barrio y ver su predicción junto con análisis detallado.
3. **Mapa de Madrid interactivo** donde cada barrio está coloreado según probabilidad de gentrificación. (4) 
4. **Visuales profesionales** incluyendo Feature Importance, curvas ROC, matriz de confusión, SHAP values y evolución temporal de TOP 3 barrios.
**Ranking TOP 10** de barrios en riesgo inmediato.
**Informe técnico** documentando arquitectura del modelo, limitaciones honestas y recomendaciones futuras. Todo el código será reproducible, documentado en  Jupyter notebooks paso a paso, y estará disponible en repositorio GitHub público.

---

## 2. Pregunta Técnica del ML

### Formulación del problema

```
Target (variable a predecir):
  GENTRIFICARÁ = [SÍ, NO]
  
Definición operativa de "gentrificará":
  - Barrio con baja renta histórica (2015-2020) que es similar a Malasaña/Chueca
  - Había poca hostelería moderna, ahora explota
  - En últimos 3 años: +40% aperturas de bares/cafeterías
  - Población creciente (joven, profesionales)
  
Features (variables de entrada):
  - Trayectoria de hostelería (54 meses)
  - Velocidad de cambio (aceleración)
  - Población absoluta y crecimiento
  - Renta media y mediana
  - Densidad comercial
  - Proporción de residentes extranjeros
  - Edad media de residentes
  - ...20-30 features más

Modelos a entrenar:
  1. Logistic Regression (baseline)
  2. SVM (kernel RBF)
  3. XGBoost (state-of-the-art)
  4. Ensamble de predicciones

Métrica primaria: F1-Score (balance Precision-Recall)
Métrica secundaria: AUC-ROC (curva completa)
```

---

## 3. Datos Disponibles - Inventario Completo
---

### Fuente 1: Censo de Locales, Actividades y Terrazas (Histórico) 

**¿Qué es?**
Registro oficial de TODOS los locales comerciales en Madrid (bares, tiendas, oficinas, etc.), sus actividades y terrazas de hostelería y restauración, actualizado mensualmente desde 2014.

**¿Dónde obtenerlo?**
- **Portal:** datos.madrid.es (Ayuntamiento de Madrid)
- **Dataset:** 209548-0-censo-locales-historico
- **URL directa:** https://datos.madrid.es/dataset/209548-0-censo-locales-historico
- **Formato:** CSV descargable directamente
- **Acceso:** Público, sin autenticación requerida

**¿Qué tengo?**
- Febrero 2022 → Junio 2026
- 54 meses continuos
- 149,937 locales únicos
- 128 barrios + 21 distritos
- 46 columnas de metadatos (descripción de epigrafe, estado del local, etc)

**¿Por qué es importante?**
Es la FUENTE PRIMARIA de features. Cada mes veo qué bares, cafeterías y restaurantes abrieron/cerraron, permitiendo identificar cuáles barrios explotan en hostelería moderna.

**Características del dataset:**
- CSV con separador `;` (punto y coma)
- Encoding UTF-8
- Estructura mensual (un archivo por mes o consolidado)
- Incluye fecha de apertura/cierre

**Riesgos detectados:**
- 39,206 registros sin descripción de epigrafe (~10% del dataset). Solución: filtrar por descripción válida
- Algunos cambios en clasificación entre años - documentados en metadatos
- Puede haber pequeños retrasos en actualización del histórico

**Calidad:** oficial Ayuntamiento, bien estructurado, confiable, estable y mantenido

**Estabilidad:** El dataset lleva en mantenimiento desde 2014, con actualizaciones regulares mensuales.

---

### Fuente 2: Padrón Municipal de Habitantes

**¿Qué es?**
Registro oficial de residentes en Madrid por zona geográfica, con información de población total, edad, nacionalidad y género.

**¿Dónde obtenerlo?**
- **Portal:** datos.madrid.es (Ayuntamiento de Madrid)
- **Dataset:** 200076 (Padrón Municipal)
- **Archivo que tengo:** 200076-2-padron-municipal-csv.csv
- **Formato:** CSV
- **Acceso:** Público, sin autenticación requerida

**¿Qué tengo?**
- Snapshot actual: Julio 2026
- Población total por sección censal
- Edad media del barrio
- Proporción de residentes extranjeros
- Distribución por género

**Limitación principal:** Solo tengo UNA foto temporal (julio 2026), no histórico mes a mes

**Cómo lo uso:**
- Como feature ESTÁTICA en el modelo (contexto demográfico del barrio)
- No como serie temporal
- Proporciona contexto sobre barrios: densidad, diversidad, edad de la población

**Calidad:** oficial Ayuntamiento, actualizado, bien estructurado
**Estabilidad:** El padrón se actualiza regularmente. Dataset disponible históricamente, aunque yo uso snapshot actual.

---

### Fuente 3: Indicadores de Renta Media y Mediana

**¿Qué es?**
Datos oficiales del Instituto Nacional de Estadística (INE) sobre ingresos promedio (renta media y mediana) por sección censal en Madrid.

**¿Dónde obtenerlo?**
- **Fuente principal:** INE (Instituto Nacional de Estadística)
- **Portal secundario:** datos.madrid.es
- **Archivo que tengo:** Indicadores-renta-media-y-mediana.csv
- **Cobertura temporal:** 2015-2023 (8 años histórico)
- **Acceso:** Público, sin autenticación requerida

**¿Qué tengo?**
- Renta media por sección censal (2015-2023)
- Renta mediana por sección censal (2015-2023)
- Datos desagregados geográficamente
- Histórico de 8 años permite ver tendencias

**Cómo lo uso:**
- **Feature para el modelo:** Renta actual del barrio
- **Para etiquetado:** Identificar barrios de "baja renta" (candidatos a gentrificación) vs "renta alta" (ya gentrificados)
- **Para validación:** Verificar correlación entre predicción ML y cambio de renta real

**Limitación:** Datos de 2023 (3 años atrás), pero tendencias de renta cambian lentamente, por lo que sigue siendo válido

**Calidad:** datos del INE, oficiales, confiables, bien documentados

**Estabilidad:** INE publica anualmente. Dataset histórico disponible y estable desde 2015.

---

### Fuente 4: Datos de Precios Inmobiliarios (Scraping)

**¿Qué es?**
Precios de transacciones inmobiliarias en Madrid compilados desde portales inmobiliarios públicos (Idealista, Fotocasa, etc) mediante scraping de informes públicos.

**¿Dónde obtenerlo?**
- **Fuente primaria:** Idealista (https://www.idealista.com)
- **Método:** Scraping de informes públicos y datos agregados
- **Archivos que tengo:** 
  - precios_madrid_idealista.csv
  - historico_precios_madrid_idealista.csv
- **Cobertura temporal:** Mayo 2025 - Abril 2026 (12 meses)
- **Acceso:** Datos compilados de informes públicos accesibles sin login

**¿Qué tengo?**
- Precios por distrito (21 zonas)
- Datos mensuales de cambios en precio de vivienda
- Histórico de 12 meses continuos
- Información sobre evolución de mercado inmobiliario

**Cómo lo uso:**
- NO para entrenar modelo predictivo (muy pocos datos = 12 meses)
- SÍ para VALIDACIÓN POST-HOC: verificar que barrios que predigo "SÍ gentrificará" realmente subieron precios
- Análisis correlacional: comparar predicción ML con cambio real de precios observado

**Limitación principal:** Solo 12 meses de datos (insuficiente para regresión, pero válido para validación)

**Riesgos detectados:**
- Datos a nivel distrito (21 zonas) no barrio individual (128 barrios) - menos granulares que ideal
- Series temporales cortas - no permiten modelado predictivo robusto
- Precios pueden variar según metodología de portales

**Solución adoptada:** Usar para validación y análisis correlacional, no para predicción

**Calidad:** datos públicos, accesibles, pero con limitaciones de granularidad y histórico

**Estabilidad:** Portales inmobiliarios son estables, pero precios pueden fluctuar con mercado

---

### Fuente 5: Límites Geográficos de Barrios de Madrid 

**¿Qué es?**
Archivo geográfico oficial con la delimitación de los 131 barrios de Madrid en formato vectorial, permitiendo mapeo y visualización espacial.

**¿Dónde obtenerlo?**
- **Portal:** datos.madrid.es (Ayuntamiento de Madrid)
- **Dataset:** 300496-0-barrios-madrid
- **URL directa:** https://datos.madrid.es/dataset/300496-0-barrios-madrid/information
- **Formato:** GeoJSON, Shapefile (SHP) o similar formato geoespacial
- **Acceso:** Público, descargable directamente

**¿Qué tengo?**
- Delimitación de 131 barrios de Madrid
- Información geográfica (polígonos, coordenadas)
- Metadata de barrios (nombre, código, etc)

**Cómo lo uso:**
- Para crear MAPA INTERACTIVO de Madrid coloreado por predicción
- Visualización espacial de resultados
- Overlay de datos con geometrías geográficas

**Importancia:** Esencial para la componente visual del proyecto (mapa coloreado)

**Calidad:** oficial Ayuntamiento, geometrías precisas, bien documentadas

**Estabilidad:** Los límites administrativos son estables. Datos mantenidos y actualizados.

---

**Conclusión:** Todas las fuentes son PÚBLICAS, ACCESIBLES y ESTABLES. No hay dependencias de pagos o permisos especiales.

---


## 6. Privacidad y Aspectos Éticos

Todos los análisis y predicciones son a nivel de BARRIO. No es posible identificar a ninguna persona.

**¿Qué datos personales tengo?**
- ❌ Censo de Locales: Solo negocios, no personas
- ❌ Padrón: Agregado por barrio (5,000+ personas), no individual
- ❌ Precios: Promedio por zona, no transacciones específicas
- ❌ Renta: Datos del INE, agregados

### ¿Es éticamente correcto predecir gentrificación?

- Es un proyecto académico, no comercial
- Los datos ya son públicos (alguien los iba a analizar igual)
- Entender un proceso no es promoverlo
- La gentrificación sucede con o sin mi modelo
- Mi valor es la TRANSPARENCIA: explicar cómo funciona

**Decisión ética adoptada:** Seré honesto sobre limitaciones y riesgos en el informe.

---

## 7. ¿Realmente puedo hacer esto? (Viabilidad)

### ¿Consigo los datos?
Sí, todos los datos estan disponibles, sin problemas de acceso.

- Censo Locales: datos.madrid.es (descarga directa)
- Padrón: datos.madrid.es
- Renta: INE (descarga directa)
- Precios: ya tengo (scraping previo)

---

### ¿Son buenos los datos?

Sí, muy buenos para clasificación

**Lo que funciona perfecto:**
- 54 meses de hostelería = dataset robusto para ML
- Barrios conocidos gentrificados = etiquetado posible
- Features suficientes y variadas
- Datos limpios y confiables

**Lo que no es perfecto:**
- Precios: solo 12 meses (pero no necesito para entrenar)
- Padrón: una foto (pero útil como contexto)
- Renta: de 2023 (antiguo pero tendencias válidas)

**Impacto:** MÍNIMO. Los datos de hostelería (lo importante) son perfectos.

---

### ¿Qué puede salir mal?

**Riesgo 1: Dataset desbalanceado**
- Problema: 85% NO gentrificará, 15% SÍ
- Solución: SMOTE o class_weight
- Probabilidad de problema: BAJA

**Riesgo 2: Overfitting**
- Problema: 128 barrios es poco para 30 features
- Solución: Validación cruzada, regularización
- Probabilidad: MEDIA (controlable)

**Riesgo 3: Features débiles**
- Problema: Quizás hostelería NO predice gentrificación bien
- Solución: Probar otros features, análisis exploratorio
- Probabilidad: BAJA (lógica subyacente es sólida)

**Veredicto:** Todos los riesgos son controlables.

---

### ¿Y si falla algo?

Tengo Plan B para cada fuente:

| Si falla... | Plan B | Viabilidad |
|---|---|---|
| Censo Locales | Google Places reviews (bares por barrio) | Alta |
| Padrón Municipal | Proyecciones INE | Alta |
| Renta INE | Datos municipales alternativos | Alta |
| Precios Idealista | No necesario (validación teórica) | Alta |

**Conclusión:** No hay punto de fallo crítico.

---