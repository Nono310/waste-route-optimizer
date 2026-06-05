import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder
import joblib
import os

print("🤖 Starting model training...\n")

# ── 1. LOAD PROCESSED DATA ────────────────────────────────────────────────────
df = pd.read_csv("data/processed/processed_data.csv")
print(f"✅ Loaded processed_data.csv — {len(df)} rows")

# ── 2. ENCODE CATEGORICAL FEATURES ───────────────────────────────────────────
le_bin = LabelEncoder()
le_neighborhood = LabelEncoder()

df["bin_id_encoded"]       = le_bin.fit_transform(df["bin_id"])
df["neighborhood_encoded"] = le_neighborhood.fit_transform(df["neighborhood"])

# ── 3. DEFINE FEATURES AND TARGET ────────────────────────────────────────────
FEATURES = [
    "bin_id_encoded",
    "neighborhood_encoded",
    "lat",
    "lon",
    "capacity_kg",
    "day_of_week",
    "hour",
    "month",
    "week_of_year",
    "is_weekend",
    "time_of_day",
    "is_market_area",
    "avg_waste_by_hour",
    "avg_waste_by_day",
    "total_collections"
]

TARGET = "fill_percentage"

X = df[FEATURES]
y = df[TARGET]

print(f"✅ Features: {len(FEATURES)}")
print(f"✅ Target  : {TARGET}")

# ── 4. TRAIN/TEST SPLIT ───────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

print(f"\n✅ Training set : {len(X_train)} samples")
print(f"✅ Test set     : {len(X_test)} samples")

# ── 5. TRAIN RANDOM FOREST ────────────────────────────────────────────────────
print("\n🌲 Training Random Forest Regressor...")

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)
print("✅ Training complete!")

# ── 6. EVALUATE MODEL ─────────────────────────────────────────────────────────
print("\n📊 Evaluating model...")

y_pred_train = model.predict(X_train)
y_pred_test  = model.predict(X_test)

mae_train  = mean_absolute_error(y_train, y_pred_train)
rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))

mae_test   = mean_absolute_error(y_test, y_pred_test)
rmse_test  = np.sqrt(mean_squared_error(y_test, y_pred_test))

print(f"\n   TRAINING SET:")
print(f"   MAE  : {mae_train:.2f}%")
print(f"   RMSE : {rmse_train:.2f}%")

print(f"\n   TEST SET:")
print(f"   MAE  : {mae_test:.2f}%")
print(f"   RMSE : {rmse_test:.2f}%")

# ── 7. FEATURE IMPORTANCE ─────────────────────────────────────────────────────
print("\n🔍 Top 5 Most Important Features:")
importances = pd.Series(model.feature_importances_, index=FEATURES)
top5 = importances.sort_values(ascending=False).head(5)
for feat, score in top5.items():
    print(f"   {feat:<25} {score:.4f}")

# ── 8. SAMPLE PREDICTIONS ─────────────────────────────────────────────────────
print("\n🔮 Sample Predictions vs Actual:")
sample = pd.DataFrame({
    "Actual":    y_test.values[:5],
    "Predicted": y_pred_test[:5].round(2)
})
print(sample.to_string(index=False))

# ── 9. SAVE MODEL AND ENCODERS ────────────────────────────────────────────────
os.makedirs("data/models", exist_ok=True)

joblib.dump(model,          "data/models/waste_model.pkl")
joblib.dump(le_bin,         "data/models/le_bin.pkl")
joblib.dump(le_neighborhood,"data/models/le_neighborhood.pkl")
joblib.dump(FEATURES,       "data/models/features.pkl")

print("\n✅ Model saved    : data/models/waste_model.pkl")
print("✅ Encoders saved : data/models/le_bin.pkl")
print("✅ Features saved : data/models/features.pkl")
print("\n🎉 Model training complete!")