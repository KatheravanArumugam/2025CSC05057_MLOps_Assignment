"""Tests for the preprocessing pipeline and data split helpers."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.features.preprocessing import (
    ALL_FEATURES,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_preprocessor,
    split_features_target,
)


def test_feature_lists_are_disjoint_and_complete():
    assert set(NUMERIC_FEATURES).isdisjoint(CATEGORICAL_FEATURES)
    assert set(ALL_FEATURES) == set(NUMERIC_FEATURES) | set(CATEGORICAL_FEATURES)


def test_split_features_target_returns_correct_shapes(sample_df: pd.DataFrame):
    X, y = split_features_target(sample_df)
    assert list(X.columns) == ALL_FEATURES
    assert len(X) == len(y) == len(sample_df)
    assert y.dtype.kind == "i"


def test_preprocessor_handles_missing_values(sample_df: pd.DataFrame):
    df = sample_df.copy()
    # Inject NaNs into a numeric and a categorical column.
    df.loc[df.index[:5], "chol"] = np.nan
    df.loc[df.index[:5], "thal"] = np.nan
    X, _ = split_features_target(df)
    pre = build_preprocessor()
    arr = pre.fit_transform(X)
    assert not np.isnan(arr).any()
    assert arr.shape[0] == len(df)
    assert arr.shape[1] >= len(NUMERIC_FEATURES)  # one-hot expands categoricals


def test_preprocessor_is_deterministic(sample_df: pd.DataFrame):
    X, _ = split_features_target(sample_df)
    a = build_preprocessor().fit_transform(X)
    b = build_preprocessor().fit_transform(X)
    assert np.allclose(a, b)


def test_preprocessor_rejects_missing_columns(sample_df: pd.DataFrame):
    X, _ = split_features_target(sample_df)
    pre = build_preprocessor().fit(X)
    bad = X.drop(columns=["age"])
    with pytest.raises(Exception):
        pre.transform(bad)
