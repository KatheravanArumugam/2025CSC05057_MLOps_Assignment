"""Download the UCI Heart Disease dataset and save it as raw/processed CSV.

Primary source: UCI ML Repository via the ``ucimlrepo`` package (id=45,
"Heart Disease"). A direct CSV mirror is used as a fallback if the
``ucimlrepo`` API is unreachable.

Outputs
-------
- ``data/raw/heart_disease_raw.csv``        : as obtained, before any cleaning.
- ``data/processed/heart_disease.csv``      : cleaned (target binarized,
  obvious missing markers replaced with NaN, no row imputation here -- that
  belongs to the modelling pipeline).

Run::

    python -m src.data.download_data
"""
from __future__ import annotations

import io
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

LOGGER = logging.getLogger("download_data")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data" / "raw" / "heart_disease_raw.csv"
PROCESSED_PATH = ROOT / "data" / "processed" / "heart_disease.csv"

# Cleveland subset is the canonical 14-attribute version used in literature.
COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num",
]
FALLBACK_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "heart-disease/processed.cleveland.data"
)


def _download_via_ucimlrepo() -> pd.DataFrame:
    from ucimlrepo import fetch_ucirepo  # imported lazily so fallback works

    LOGGER.info("Fetching UCI Heart Disease (id=45) via ucimlrepo ...")
    ds = fetch_ucirepo(id=45)
    features = ds.data.features
    target = ds.data.targets
    df = pd.concat([features, target], axis=1)
    # Standardise the target column name to ``num`` (matches the original UCI).
    target_col = target.columns[0]
    if target_col != "num":
        df = df.rename(columns={target_col: "num"})
    return df


def _download_via_http() -> pd.DataFrame:
    LOGGER.warning("ucimlrepo unavailable; falling back to direct HTTP CSV.")
    resp = requests.get(FALLBACK_URL, timeout=30)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text), header=None, names=COLUMNS, na_values="?")
    return df


def download() -> pd.DataFrame:
    try:
        df = _download_via_ucimlrepo()
    except Exception as exc:  # pragma: no cover - network fallback
        LOGGER.warning("ucimlrepo failed (%s); using HTTP fallback.", exc)
        df = _download_via_http()
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Light cleaning: harmonise missing markers and binarise the target."""
    df = df.copy()
    # UCI uses '?' as a missing marker for ``ca`` and ``thal``.
    df = df.replace({"?": np.nan})
    for col in ("ca", "thal"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Binarise the target: 0 = no disease, >=1 = disease present.
    df["target"] = (df["num"].astype(float) > 0).astype(int)
    df = df.drop(columns=["num"])
    return df


def main() -> int:
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw_df = download()
    raw_df.to_csv(RAW_PATH, index=False)
    LOGGER.info("Saved raw  -> %s  (shape=%s)", RAW_PATH, raw_df.shape)

    clean_df = clean(raw_df)
    clean_df.to_csv(PROCESSED_PATH, index=False)
    LOGGER.info("Saved clean -> %s  (shape=%s)", PROCESSED_PATH, clean_df.shape)
    LOGGER.info("Class balance:\n%s", clean_df["target"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
