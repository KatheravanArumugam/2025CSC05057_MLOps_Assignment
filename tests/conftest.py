"""Shared pytest fixtures."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed" / "heart_disease.csv"


@pytest.fixture(scope="session")
def sample_df() -> pd.DataFrame:
    """Use real data when available, else fall back to a small synthetic frame."""
    if PROCESSED.exists():
        return pd.read_csv(PROCESSED)

    rng = np.random.default_rng(0)
    n = 60
    return pd.DataFrame({
        "age": rng.integers(30, 80, n),
        "sex": rng.integers(0, 2, n),
        "cp": rng.integers(0, 4, n),
        "trestbps": rng.integers(90, 180, n),
        "chol": rng.integers(120, 320, n),
        "fbs": rng.integers(0, 2, n),
        "restecg": rng.integers(0, 3, n),
        "thalach": rng.integers(80, 200, n),
        "exang": rng.integers(0, 2, n),
        "oldpeak": rng.uniform(0, 5, n).round(1),
        "slope": rng.integers(0, 3, n),
        "ca": rng.integers(0, 4, n).astype(float),
        "thal": rng.choice([3.0, 6.0, 7.0], n),
        "target": rng.integers(0, 2, n),
    })


@pytest.fixture
def sample_payload() -> dict:
    return {
        "age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233,
        "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0,
        "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1,
    }
