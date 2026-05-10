"""End-to-end tests for the FastAPI service using FastAPI TestClient."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "heart_disease_model.pkl"


@pytest.fixture(scope="module")
def client():
    if not MODEL_PATH.exists():
        pytest.skip("Trained model missing. Run `python -m src.models.train`.")
    from src.api.app import app  # imported lazily to allow skipping

    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "heart-disease-api"


def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_predict_returns_well_formed_response(client, sample_payload):
    r = client.post("/predict", json=sample_payload)
    assert r.status_code == 200
    body = r.json()
    assert body["prediction"] in (0, 1)
    assert body["label"] in ("disease", "no_disease")
    assert 0.0 <= body["confidence"] <= 1.0
    assert len(body["probabilities"]) == 2
    assert abs(sum(body["probabilities"]) - 1.0) < 1e-6


def test_predict_validates_input(client, sample_payload):
    bad = dict(sample_payload)
    bad.pop("age")
    r = client.post("/predict", json=bad)
    assert r.status_code == 422  # Pydantic validation error


def test_metrics_endpoint(client, sample_payload):
    # Make a prediction so a counter is incremented.
    client.post("/predict", json=sample_payload)
    r = client.get("/metrics")
    assert r.status_code == 200
    text = r.text
    assert "heart_disease_predictions_total" in text
