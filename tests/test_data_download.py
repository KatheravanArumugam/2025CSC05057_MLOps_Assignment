"""Tests for the data acquisition / cleaning pipeline (offline-friendly)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.download_data import COLUMNS, clean


def test_clean_replaces_question_marks_and_binarises_target():
    raw = pd.DataFrame(
        [
            [63, 1, 3, 145, 233, 1, 0, 150, 0, 2.3, 0, "0", "?", 0],
            [67, 1, 0, 160, 286, 0, 0, 108, 1, 1.5, 1, "?", "3", 2],
            [50, 0, 2, 120, 219, 0, 1, 158, 0, 1.6, 1, "0", "3", 0],
        ],
        columns=COLUMNS,
    )
    out = clean(raw)
    # `num` is dropped, `target` is created.
    assert "target" in out.columns and "num" not in out.columns
    # Target is binary in {0, 1}.
    assert set(out["target"].unique()).issubset({0, 1})
    # '?' values converted to NaN in `ca` / `thal`.
    assert np.isnan(out.iloc[0]["thal"])
    assert np.isnan(out.iloc[1]["ca"])
    # Binarisation: num=2 -> target=1, num=0 -> target=0.
    assert list(out["target"]) == [0, 1, 0]


def test_clean_does_not_mutate_input():
    raw = pd.DataFrame(
        [[1] * 13 + [0]],
        columns=COLUMNS,
    )
    before = raw.copy(deep=True)
    _ = clean(raw)
    pd.testing.assert_frame_equal(raw, before)
