"""
SCRIPT 5 MEJORADO
Entrena ENSEMBLE (SVM + RF + XGBoost) SIN SMOTE + CalibratedClassifierCV
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.calibration import CalibratedClassifierCV
import pickle
import json

print("=" * 100)
print("SCRIPT 5 MEJORADO: ENSEMBLE SIN SMOTE + CALIBRACIÓN")
print("=" * 100)

# ============================================================================
# 1. CARGAR DATOS
# ============================================================================

print("\n1. Cargando datos...\n")

df_gold = pd.read_parquet('data/gold/gold_barrios_enriquecido_test.parquet')
print(f"GOLD: {len(df_gold)} barrios × {len(df_gold.columns)} columnas")

with open('data/04_train_test/feature_names_v2_mejorado.json', 'r') as f:
    feature_names = json.load(f)
print(f"Features: {len(feature_names)}")

X = df_gold[feature_names]
y = df_gold['gentrificara']

print(f"\n   Dataset:")
print(f"   • Total: {len(X)}")
print(f"   • SÍ: {(y == 1).sum()} ({100*(y==1).mean():.1f}%)")
print(f"   • NO: {(y == 0).sum()} ({100*(y==0).mean():.1f}%)")

# ============================================================================
# 2. ESCALAR
# ============================================================================

print("\n2. Escalando features...\n")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("Features escalados")

# ============================================================================
# 3. ENSEMBLE MEJORADO (SIN SMOTE)
# ============================================================================

print("\n3. Entrenando ENSEMBLE MEJORADO...\n")

# Modelos individuales con class_weight para dataset desbalanceado
svm_modelo = SVC(
    kernel='rbf', 
    C=1.0,  # Más bajo que antes para mejor generalización
    gamma=0.001,  # Más bajo para penalizar complejidad
    probability=True,
    class_weight='balanced',
    random_state=42
)

rf_modelo = RandomForestClassifier(
    n_estimators=150,  # Más árboles
    max_depth=8,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

gb_modelo = GradientBoostingClassifier(
    n_estimators=150,
    learning_rate=0.05,  # Más bajo para regularización
    max_depth=4,
    min_samples_split=5,
    min_samples_leaf=2,
    subsample=0.8,
    random_state=42
)

# Ensemble sin calibración primero
ensemble_base = VotingClassifier(
    estimators=[
        ('svm', svm_modelo),
        ('rf', rf_modelo),
        ('gb', gb_modelo)
    ],
    voting='soft',
    weights=[1, 1, 1]
)

# Entrenar ensemble base
ensemble_base.fit(X_scaled, y)
print("Ensemble base entrenado")

# CALIBRAR probabilidades con Platt scaling
ensemble_calibrated = CalibratedClassifierCV(
    estimator=ensemble_base,
    method='sigmoid',  # Platt scaling
    cv=5
)
ensemble_calibrated.fit(X_scaled, y)
print("Ensemble calibrado con CalibratedClassifierCV")

# ============================================================================
# 4. VALIDACIÓN CRUZADA
# ============================================================================

print("\n4. Validación Cruzada (5-Fold Stratified)...\n")

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores_auc = cross_val_score(ensemble_calibrated, X_scaled, y, cv=cv, scoring='roc_auc')
scores_f1 = cross_val_score(ensemble_calibrated, X_scaled, y, cv=cv, scoring='f1')
scores_acc = cross_val_score(ensemble_calibrated, X_scaled, y, cv=cv, scoring='accuracy')

print(f"   AUC-ROC:  {scores_auc.mean():.4f} ± {scores_auc.std():.4f}")
print(f"   F1-Score: {scores_f1.mean():.4f} ± {scores_f1.std():.4f}")
print(f"   Accuracy: {scores_acc.mean():.4f} ± {scores_acc.std():.4f}")

# ============================================================================
# 5. GUARDAR MODELOS
# ============================================================================

print("\n5. Guardando modelos...\n")

with open('data/04_train_test/scaler_v2_mejorado.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("scaler_v2_mejorado.pkl")

with open('data/04_train_test/modelo_ensemble_v2_mejorado.pkl', 'wb') as f:
    pickle.dump(ensemble_calibrated, f)
print("modelo_ensemble_v2_mejorado.pkl")

with open('data/04_train_test/feature_names_v2_mejorado.json', 'w') as f:
    json.dump(feature_names, f)
print("feature_names_v2_mejorado.json")

# ============================================================================
# 6. VERIFICACIÓN DE PREDICCIONES
# ============================================================================

print("\n6. Verificando predicciones...\n")

probs = ensemble_calibrated.predict_proba(X_scaled)[:, 1]

print(f"   Distribución de probabilidades:")
print(f"   • Mínima:  {probs.min():.4f}")
print(f"   • Máxima:  {probs.max():.4f}")
print(f"   • Media:   {probs.mean():.4f}")
print(f"   • Mediana: {np.median(probs):.4f}")

# Percentiles
p33 = np.percentile(probs, 33)
p67 = np.percentile(probs, 67)

bajo = (probs <= p33).sum()
medio = ((probs > p33) & (probs <= p67)).sum()
alto = (probs > p67).sum()

print(f"\n   Conteo AUTOMÁTICO con percentiles:")
print(f"   • Percentil 33: {p33:.4f}")
print(f"   • Percentil 67: {p67:.4f}")
print(f"   • BAJO  (<{p33:.2f}):  {bajo:3d} ({100*bajo/len(probs):5.1f}%)")
print(f"   • MEDIO ({p33:.2f}-{p67:.2f}): {medio:3d} ({100*medio/len(probs):5.1f}%)")
print(f"   • ALTO  (>{p67:.2f}):  {alto:3d} ({100*alto/len(probs):5.1f}%)")

print("\n" + "=" * 100)
print("COMPLETADO - MODELO MEJORADO LISTO")
print("=" * 100)
print("""
ARCHIVOS GENERADOS:
  - modelo_ensemble_v2_mejorado.pkl
  - scaler_v2_mejorado.pkl
  - feature_names_v2_mejorado.json
""")
