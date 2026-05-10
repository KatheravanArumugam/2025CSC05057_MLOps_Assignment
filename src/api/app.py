"""FastAPI service exposing the trained heart-disease classifier.

Endpoints
---------
GET  /          : service information.
GET  /health    : liveness/readiness probe (returns 200 once the model is loaded).
POST /predict   : JSON in, prediction + confidence out.
GET  /metrics   : Prometheus metrics (request count, latency, prediction counts).
"""
from __future__ import annotations

import logging
import os
import pickle
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.schemas import PatientFeatures, PredictionResponse
from src.features.preprocessing import ALL_FEATURES

LOGGER = logging.getLogger("api")
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format='{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
)

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = Path(os.environ.get("MODEL_PATH", ROOT / "models" / "heart_disease_model.pkl"))
MODEL_VERSION = os.environ.get("MODEL_VERSION", "v1")

PRED_COUNTER = Counter(
    "heart_disease_predictions_total",
    "Total predictions served, labelled by predicted class.",
    labelnames=("prediction",),
)
PRED_LATENCY = Histogram(
    "heart_disease_prediction_latency_seconds",
    "Latency of /predict in seconds.",
)

_state: Dict[str, Any] = {"model": None}


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Model file not found at {MODEL_PATH}. Run `python -m src.models.train` first."
        )
    with MODEL_PATH.open("rb") as f:
        _state["model"] = pickle.load(f)
    LOGGER.info("Model loaded from %s", MODEL_PATH)
    yield
    _state.clear()


app = FastAPI(
    title="Heart Disease Risk Prediction API",
    description="Predicts the probability of heart disease from patient features.",
    version=MODEL_VERSION,
    lifespan=lifespan,
)

# Default Prometheus middleware: HTTP latency, status codes, in-flight requests.
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "service": "heart-disease-api",
        "model_version": MODEL_VERSION,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }


@app.get("/health")
def health() -> Dict[str, str]:
    if _state.get("model") is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    return {"status": "ok", "model_version": MODEL_VERSION}


@app.post("/predict", response_model=PredictionResponse)
def predict(features: PatientFeatures) -> PredictionResponse:
    model = _state.get("model")
    if model is None:
        raise HTTPException(status_code=503, detail="Model not ready")

    start = time.perf_counter()
    row = pd.DataFrame([features.model_dump()])[ALL_FEATURES]
    probs = model.predict_proba(row)[0]
    pred = int(probs.argmax())
    confidence = float(probs[pred])
    PRED_LATENCY.observe(time.perf_counter() - start)
    PRED_COUNTER.labels(prediction=str(pred)).inc()

    LOGGER.info(
        "prediction served pred=%s confidence=%.4f model_version=%s",
        pred, confidence, MODEL_VERSION,
    )
    return PredictionResponse(
        prediction=pred,
        label="disease" if pred == 1 else "no_disease",
        confidence=confidence,
        probabilities=[float(p) for p in probs],
        model_version=MODEL_VERSION,
    )
