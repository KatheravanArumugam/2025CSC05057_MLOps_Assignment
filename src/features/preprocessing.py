"""Reproducible preprocessing pipeline for the Heart Disease dataset.

Builds a single ``sklearn`` ``Pipeline`` that:
  * imputes numeric columns with the median,
  * imputes & one-hot encodes categorical columns,
  * standard-scales numeric columns.

The same object is fitted during training and reused at inference time so
training/serving skew cannot occur.
"""
from __future__ import annotations

from typing import List, Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Feature definitions (order matters for the API schema).
NUMERIC_FEATURES: List[str] = ["age", "trestbps", "chol", "thalach", "oldpeak", "ca"]
CATEGORICAL_FEATURES: List[str] = ["sex", "cp", "fbs", "restecg", "exang", "slope", "thal"]
ALL_FEATURES: List[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET: str = "target"


def build_preprocessor() -> ColumnTransformer:
    """Return an unfitted ColumnTransformer combining numeric + categorical steps."""
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERIC_FEATURES),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def split_features_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Return X (features in canonical order) and y (target)."""
    X = df[ALL_FEATURES].copy()
    y = df[TARGET].astype(int).copy()
    return X, y
