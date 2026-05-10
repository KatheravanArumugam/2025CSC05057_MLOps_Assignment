"""Tests for the trained model artefact."""
from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
import pytest

from src.features.preprocessing import ALL_FEATURES

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "heart_disease_model.pkl"


@pytest.fixture(scope="module")
def model():
    if not MODEL_PATH.exists():
        pytest.skip(
            "Trained model not present. Run `python -m src.models.train` first."
        )
    with MODEL_PATH.open("rb") as f:
        return pickle.load(f)


def test_model_loads_and_has_expected_steps(model):
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")
    # Sklearn Pipeline introspection.
    assert "preprocessor" in dict(model.named_steps)
    assert "model" in dict(model.named_steps)


def test_model_accepts_canonical_feature_order(model, sample_payload):
    row = pd.DataFrame([sample_payload])[ALL_FEATURES]
    pred = model.predict(row)
    proba = model.predict_proba(row)
    assert pred.shape == (1,)
    assert proba.shape == (1, 2)
    assert 0.0 <= float(proba[0].max()) <= 1.0
    assert int(pred[0]) in (0, 1)
