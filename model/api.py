from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import subprocess
from typing import Optional
import json
from pathlib import Path

# =====================
# PATH CONFIG
# =====================
BASE_DIR = Path(r"C:\Users\USER\Desktop\BI-DM Project")

MODEL_PATH = BASE_DIR / "model" / "co2_model.pkl"
MODEL_SCRIPT = BASE_DIR / "model" / "model.py"
METRICS_PATH = BASE_DIR / "model" / "model_metrics.json"
HISTORY_PATH = BASE_DIR / "data" / "Cleansing_zone" / "clean_data.csv"

# =====================
# APP INIT
# =====================
app = FastAPI(
    title="CO2 Prediction API",
    version="1.2",
    description="API for CO₂ Emissions Prediction, History & Model Performance"
)

# =====================
# CORS
# =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# LOADERS
# =====================
def load_model():
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        print("❌ Model load failed:", e)
        return None

def load_history():
    try:
        return pd.read_csv(HISTORY_PATH)
    except Exception as e:
        print("❌ History load failed:", e)
        return pd.DataFrame()

def load_metrics():
    if not METRICS_PATH.exists():
        return None
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

model = load_model()
history_df = load_history()
metrics = load_metrics()

# =====================
# SCHEMA
# =====================
class PredictRequest(BaseModel):
    country: str
    year: int

# =====================
# HEALTH CHECK
# =====================
@app.get("/health")
def health_check():
    return {
        "model_loaded": model is not None,
        "history_rows": len(history_df),
        "metrics_loaded": metrics is not None
    }

# =====================
# COUNTRIES
# =====================
@app.get("/countries")
def get_countries():
    if history_df.empty:
        raise HTTPException(status_code=500, detail="History not loaded")

    countries = sorted(history_df["country"].unique().tolist())
    return {"countries": countries}

# =====================
# MODEL PERFORMANCE ✅ (FIXED)
# =====================
@app.get("/model/performance")
def get_model_performance():
    if metrics is None:
        raise HTTPException(status_code=404, detail="Metrics not found")

    return {
        "rmse": metrics["rmse"],
        "r2": metrics["r2"],
        "rows": metrics.get("rows", 0)
    }

# =====================
# PREDICT
# =====================
@app.post("/predict")
def predict(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    input_df = pd.DataFrame(0, index=[0], columns=model.feature_names_in_)
    input_df.loc[0, "year"] = req.year

    country_col = f"country_{req.country}"
    if country_col not in input_df.columns:
        raise HTTPException(status_code=400, detail="Country not supported")

    input_df.loc[0, country_col] = 1

    prediction = model.predict(input_df)[0]

    return {
        "country": req.country,
        "year": req.year,
        "predicted_co2": int(round(prediction)),
        "unit": "MtCO2"
    }

# =====================
# HISTORY
# =====================
@app.get("/history/{country}")
def get_history(
    country: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None
):
    df = history_df[history_df["country"] == country].copy()
    if df.empty:
        raise HTTPException(status_code=404, detail="Country not found")

    start_year = start_year or int(df["year"].min())
    end_year = end_year or int(df["year"].max())

    df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
    df["co2"] = df["co2"].round(0).astype(int)

    return {
        "country": country,
        "unit": "MtCO2",
        "records": df.sort_values("year").to_dict(orient="records")
    }

# =====================
# RETRAIN
# =====================
@app.post("/retrain")
def retrain_model():
    global model, history_df, metrics

    result = subprocess.run(
        ["python", str(MODEL_SCRIPT)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)

    model = load_model()
    history_df = load_history()
    metrics = load_metrics()

    return {"status": "success"}