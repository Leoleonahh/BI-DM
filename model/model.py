# model/model.py
import pandas as pd
import joblib
import json
from pathlib import Path

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
df = load_training_data()

if df.empty:
    raise ValueError("Training data is empty")

# =====================
# FEATURE ENGINEERING
# =====================
df_encoded = pd.get_dummies(df, columns=["country"])

X = df_encoded.drop(columns=["co2"])
y = df_encoded["co2"]

# =====================
# TRAIN / TEST SPLIT
# =====================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =====================
# TRAIN MODEL
# =====================
model = LinearRegression()
model.fit(X_train, y_train)

# =====================
# EVALUATION
# =====================
y_pred = model.predict(X_test)

rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

# 👉 Accuracy แบบ Regression
mean_y = y_test.mean()
accuracy = max(0, (1 - rmse / mean_y) * 100)

# =====================
# SAVE MODEL
# =====================
joblib.dump(model, MODEL_PATH)

# =====================
# SAVE METRICS
# =====================
metrics = {
    "rmse": round(rmse, 2),
    "r2": round(r2, 4),
    "accuracy": round(accuracy, 2)
}

with open(METRICS_PATH, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print("Model retrained successfully")