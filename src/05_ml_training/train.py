"""
SCRIPT 5 CORREGIDO
Entrena ENSEMBLE con Calibración Isotónica y Umbrales Absolutos de Riesgo
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
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# ============================================================================
# 1. CARGAR DATOS
# ============================================================================
df_gold = pd.read_parquet('data/gold/gold_barrios_enriquecido_test.parquet')

with open('data/04_train_test/feature_names_v2_mejorado.json', 'r') as f:
    feature_names = json.load(f)

X = df_gold[feature_names]
y = df_gold['gentrificara']

# ============================================================================
# 2. ESCALAR
# ============================================================================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ============================================================================
# 3. ENSEMBLE MEJORADO
# ============================================================================
svm_modelo = SVC(
    kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42
)

rf_modelo = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    min_samples_split=4,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1,
)

gb_modelo = GradientBoostingClassifier(
    n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42
)

ensemble_base = VotingClassifier(
    estimators=[('svm', svm_modelo), ('rf', rf_modelo), ('gb', gb_modelo)],
    voting='soft',
)

# Calibración Isotónica (distribución más continua entre 0 y 1)
ensemble_calibrated = CalibratedClassifierCV(
    estimator=ensemble_base, method='isotonic', cv=3
)
ensemble_calibrated.fit(X_scaled, y)

# ============================================================================
# 4. EVALUACIÓN Y PREDICCIONES
# ============================================================================
probs = ensemble_calibrated.predict_proba(X_scaled)[:, 1]

# UMBRALES ABSOLUTOS DE NEGOCIO (No Percentiles)
UMBRAL_BAJO = 0.35
UMBRAL_ALTO = 0.65

bajo = (probs < UMBRAL_BAJO).sum()
medio = ((probs >= UMBRAL_BAJO) & (probs <= UMBRAL_ALTO)).sum()
alto = (probs > UMBRAL_ALTO).sum()

print(f'\nDistribución Real de Probabilidades:')
print(f' • Mínima: {probs.min():.4f} | Máxima: {probs.max():.4f}')
print(f' • Media:  {probs.mean():.4f} | Mediana: {np.median(probs):.4f}')

print(f'\nCategorización por Umbrales Absolutos:')
print(
    f' • BAJO  (<{UMBRAL_BAJO*100}%): {bajo} barrios ({100*bajo/len(probs):.1f}%)'
)
print(
    f' • MEDIO ({UMBRAL_BAJO*100}%-{UMBRAL_ALTO*100}%): {medio} barrios ({100*medio/len(probs):.1f}%)'
)
print(
    f' • ALTO  (>{UMBRAL_ALTO*100}%): {alto} barrios ({100*alto/len(probs):.1f}%)'
)

# ============================================================================
# 5. GUARDAR ARTEFACTOS
# ============================================================================
with open('data/04_train_test/scaler_v2_mejorado.pkl', 'wb') as f:
    pickle.dump(scaler, f)

with open('data/04_train_test/modelo_ensemble_v2_mejorado.pkl', 'wb') as f:
    pickle.dump(ensemble_calibrated, f)