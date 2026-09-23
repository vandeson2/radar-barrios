"""
SCRIPT 5 MEJORADO PARA TFM
Evaluación Comparativa de Múltiples Modelos vs. Ensemble Calibrado
"""

import json
import pickle
import numpy as np
import pandas as pd

from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# ============================================================================
# 1. CARGAR DATOS
# ============================================================================
df_gold = pd.read_parquet('data/gold/gold_barrios_enriquecido_test.parquet')

with open('data/04_train_test/feature_names_v2_mejorado.json', 'r') as f:
    feature_names = json.load(f)

X = df_gold[feature_names].apply(pd.to_numeric, errors='coerce').fillna(0.0)
y = df_gold['gentrificara']

print(f"Dataset cargado: {X.shape[0]} barrios y {X.shape[1]} características.")
print(f"Distribución del target: {y.value_counts(normalize=True).to_dict()}")

# ============================================================================
# 2. ESCALAR
# ============================================================================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ============================================================================
# 3. DEFINIR CANDIDATOS Y LÍNEA BASE (BASELINE)
# ============================================================================
modelos_candidatos = {
    '1. Regresión Logística (Baseline)': LogisticRegression(
        random_state=42, max_iter=1000
    ),
    '2. SVM (RBF Kernel)': SVC(
        kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42
    ),
    '3. Random Forest': RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        min_samples_split=4,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
    ),
    '4. Gradient Boosting': GradientBoostingClassifier(
        n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42
    ),
}

# Crear el Ensemble a partir de los modelos individuales
ensemble_base = VotingClassifier(
    estimators=[
        ('svm', modelos_candidatos['2. SVM (RBF Kernel)']),
        ('rf', modelos_candidatos['3. Random Forest']),
        ('gb', modelos_candidatos['4. Gradient Boosting']),
    ],
    voting='soft',
)

# Añadir el Ensemble no calibrado y calibrado a la lista para comparar
modelos_candidatos['5. Ensemble Base (Voting Soft)'] = ensemble_base

# ============================================================================
# 4. COMPARATIVA DE MODELOS MEDIANTE VALIDACIÓN CRUZADA (3-FOLD)
# ============================================================================
print("\n" + "=" * 80)
print(" 📊 EVALUACIÓN COMPARATIVA DE MODELOS (Stratified K-Fold CV, K=3)")
print("=" * 80)

skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
scoring = ['roc_auc', 'f1', 'precision', 'recall', 'accuracy']

resultados = []

for nombre, model in modelos_candidatos.items():
    cv_results = cross_validate(
        model, X_scaled, y, cv=skf, scoring=scoring, n_jobs=-1
    )

    resultados.append({
        'Modelo': nombre,
        'ROC-AUC': cv_results['test_roc_auc'].mean(),
        'F1-Score': cv_results['test_f1'].mean(),
        'Precision': cv_results['test_precision'].mean(),
        'Recall': cv_results['test_recall'].mean(),
        'Accuracy': cv_results['test_accuracy'].mean(),
    })

# Convertir a DataFrame y mostrar ordenado por ROC-AUC
df_comparativa = (
    pd.DataFrame(resultados)
    .sort_values(by='ROC-AUC', ascending=False)
    .reset_index(drop=True)
)
print("\n", df_comparativa.to_string(index=False))

# Guardar la tabla comparativa para la memoria del TFM
df_comparativa.to_csv(
    'data/04_train_test/comparativa_modelos_tfm.csv', index=False
)
print("\n💾 Tabla comparativa guardada en 'data/04_train_test/comparativa_modelos_tfm.csv'")

# ============================================================================
# 5. CALIBRACIÓN SIGMOIDE Y ENTRENAMIENTO FINAL
# ============================================================================
print("\n" + "=" * 80)
print(" ⚙️ ENTRENAMIENTO Y CALIBRACIÓN DEL MODELO FINAL (ENSEMBLE)")
print("=" * 80)

ensemble_calibrated = CalibratedClassifierCV(
    estimator=ensemble_base, method='sigmoid', cv=skf
)
ensemble_calibrated.fit(X_scaled, y)

# ============================================================================
# 6. EVALUACIÓN Y PREDICCIONES DEL MODELO FINAL
# ============================================================================
probs = ensemble_calibrated.predict_proba(X_scaled)[:, 1]

UMBRAL_BAJO = 0.35
UMBRAL_ALTO = 0.65

bajo = (probs < UMBRAL_BAJO).sum()
medio = ((probs >= UMBRAL_BAJO) & (probs <= UMBRAL_ALTO)).sum()
alto = (probs > UMBRAL_ALTO).sum()

print('\n--- RESULTADOS DE LAS PREDICCIONES EN EL MODELO FINAL ---')
print(f' • Mínima: {probs.min():.4f} | Máxima: {probs.max():.4f}')
print(f' • Media:  {probs.mean():.4f} | Mediana: {np.median(probs):.4f}')
print(f' • Desviación Estándar: {probs.std():.4f}')

print(f'\nCategorización por Umbrales Absolutos:')
print(
    f' • BAJO  (<{UMBRAL_BAJO*100:.0f}%): {bajo} barrios ({100*bajo/len(probs):.1f}%)'
)
print(
    f' • MEDIO ({UMBRAL_BAJO*100:.0f}%-{UMBRAL_ALTO*100:.0f}%): {medio} barrios ({100*medio/len(probs):.1f}%)'
)
print(
    f' • ALTO  (>{UMBRAL_ALTO*100:.0f}%): {alto} barrios ({100*alto/len(probs):.1f}%)'
)

# ============================================================================
# 7. GUARDAR ARTEFACTOS
# ============================================================================
with open('data/04_train_test/scaler_v2_mejorado.pkl', 'wb') as f:
    pickle.dump(scaler, f)

with open('data/04_train_test/modelo_ensemble_v2_mejorado.pkl', 'wb') as f:
    pickle.dump(ensemble_calibrated, f)

print("\n✅ Artefactos exportados correctamente.")