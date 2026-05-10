"""Generate EDA figures for the Heart Disease dataset.

Run::

    python -m src.data.eda

Outputs PNG figures to ``reports/figures/eda/``.
"""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

LOGGER = logging.getLogger("eda")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "processed" / "heart_disease.csv"
OUT = ROOT / "reports" / "figures" / "eda"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)
    sns.set_theme(style="whitegrid")

    # 1) Class balance.
    fig, ax = plt.subplots(figsize=(5, 4))
    counts = df["target"].value_counts().sort_index()
    sns.barplot(x=counts.index.map({0: "no_disease", 1: "disease"}), y=counts.values, ax=ax)
    ax.set_title("Target class balance")
    ax.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(OUT / "class_balance.png", dpi=120)
    plt.close(fig)

    # 2) Histograms of numeric features by target.
    numeric = ["age", "trestbps", "chol", "thalach", "oldpeak"]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    for ax, col in zip(axes.flat, numeric):
        sns.histplot(data=df, x=col, hue="target", kde=True, bins=25, ax=ax)
        ax.set_title(col)
    for ax in axes.flat[len(numeric):]:
        ax.set_visible(False)
    fig.suptitle("Distribution of numeric features by target")
    fig.tight_layout()
    fig.savefig(OUT / "histograms.png", dpi=120)
    plt.close(fig)

    # 3) Correlation heatmap.
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(df.corr(numeric_only=True), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Feature correlation heatmap")
    fig.tight_layout()
    fig.savefig(OUT / "correlation_heatmap.png", dpi=120)
    plt.close(fig)

    # 4) Missing values per column.
    miss = df.isna().sum().sort_values(ascending=False)
    miss = miss[miss > 0]
    if not miss.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=miss.values, y=miss.index, ax=ax, color="#cc4c4c")
        ax.set_title("Missing values per column")
        ax.set_xlabel("count")
        fig.tight_layout()
        fig.savefig(OUT / "missing_values.png", dpi=120)
        plt.close(fig)

    # 5) Categorical feature vs target.
    cats = ["sex", "cp", "fbs", "restecg", "exang", "slope", "thal"]
    fig, axes = plt.subplots(2, 4, figsize=(15, 7))
    for ax, col in zip(axes.flat, cats):
        sns.countplot(data=df, x=col, hue="target", ax=ax)
        ax.set_title(col)
    for ax in axes.flat[len(cats):]:
        ax.set_visible(False)
    fig.suptitle("Categorical feature counts by target")
    fig.tight_layout()
    fig.savefig(OUT / "categorical_vs_target.png", dpi=120)
    plt.close(fig)

    LOGGER.info("EDA figures written to %s", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
