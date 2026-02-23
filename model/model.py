# model/model.py
import pandas as pd
import joblib
import json
from pathlib import Path
from math import sqrt

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

from data_loader import load_training_data

# =====================
# PATH CONFIG
# =====================
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "co2_model.pkl"
METRICS_PATH = BASE_DIR / "model_metrics.json"

# =====================
# LOAD DATA
# =====================
print("Loading training data from database...")
df = load_training_data()

if df.empty:
    raise ValueError("Training data is empty")

required_cols = {"country", "year", "co2"}
if not required_cols.issubset(df.columns):
    raise ValueError(f"Missing required columns: {required_cols}")

# =====================
# FEATURE ENGINEERING
# =====================
print("Encoding features...")
df_encoded = pd.get_dummies(df, columns=["country"])

X = df_encoded.drop(columns=["co2"])
y = df_encoded["co2"]

# =====================
# TRAIN / TEST SPLIT
# =====================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# =====================
# TRAIN MODEL
# =====================
print("Training Linear Regression model...")
model = LinearRegression()
model.fit(X_train, y_train)

# =====================
# EVALUATION
# =====================
print("Evaluating model...")
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
rmse = sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"RMSE: {rmse:.2f}")
print(f"R2  : {r2:.4f}")

# =====================
# SAVE MODEL
# =====================
joblib.dump(model, MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")

# =====================
# SAVE METRICS
# =====================
metrics = {
    "rmse": round(rmse, 2),
    "r2": round(r2, 4),
    "rows": int(len(df)),
    "features": list(X.columns)
}

with open(METRICS_PATH, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print("Metrics saved")
print("Model retrained successfully")