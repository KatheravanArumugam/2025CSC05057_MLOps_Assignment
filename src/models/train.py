"""Train Logistic Regression and Random Forest classifiers on the
Heart Disease dataset, log everything to MLflow, and persist the best
model + preprocessing pipeline as a single pickle for serving.

Run::

    python -m src.models.train
"""
from __future__ import annotations

import json
import logging
import pickle
from pathlib import Path
from typing import Any, Dict, Tuple

import matplotlib

matplotlib.use("Agg")  # non-interactive backend; safe in CI/Docker

import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline

from src.features.preprocessing import (
    ALL_FEATURES,
    build_preprocessor,
    split_features_target,
)

LOGGER = logging.getLogger("train")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "processed" / "heart_disease.csv"
MODEL_PATH = ROOT / "models" / "heart_disease_model.pkl"
METRICS_PATH = ROOT / "models" / "metrics.json"
MLFLOW_DIR = ROOT / "mlruns"
EXPERIMENT_NAME = "heart-disease-classification"
RANDOM_STATE = 42


def _evaluate(model: Pipeline, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
    """Return common binary classification metrics on a held-out set."""
    pred = model.predict(X)
    proba = model.predict_proba(X)[:, 1]
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "precision": float(precision_score(y, pred)),
        "recall": float(recall_score(y, pred)),
        "f1": float(f1_score(y, pred)),
        "roc_auc": float(roc_auc_score(y, proba)),
    }


def _log_plots(model: Pipeline, X: pd.DataFrame, y: pd.Series, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    cm_path = out_dir / "confusion_matrix.png"
    ConfusionMatrixDisplay.from_estimator(model, X, y, cmap="Blues")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(cm_path, dpi=120)
    plt.close()
    mlflow.log_artifact(str(cm_path), artifact_path="plots")

    roc_path = out_dir / "roc_curve.png"
    RocCurveDisplay.from_estimator(model, X, y)
    plt.title("ROC Curve")
    plt.tight_layout()
    plt.savefig(roc_path, dpi=120)
    plt.close()
    mlflow.log_artifact(str(roc_path), artifact_path="plots")


def _train_one(
    name: str,
    estimator,
    param_grid: Dict[str, Any],
    X_tr: pd.DataFrame,
    y_tr: pd.Series,
    X_te: pd.DataFrame,
    y_te: pd.Series,
    cv: StratifiedKFold,
    plots_root: Path,
) -> Tuple[Pipeline, Dict[str, float]]:
    pipe = Pipeline([("preprocessor", build_preprocessor()), ("model", estimator)])
    grid = GridSearchCV(pipe, param_grid=param_grid, cv=cv, scoring="roc_auc", n_jobs=-1)

    with mlflow.start_run(run_name=name, nested=True):
        grid.fit(X_tr, y_tr)
        best = grid.best_estimator_
        cv_score = float(grid.best_score_)
        test_metrics = _evaluate(best, X_te, y_te)

        mlflow.log_param("model_family", name)
        for k, v in grid.best_params_.items():
            mlflow.log_param(k, v)
        mlflow.log_metric("cv_roc_auc", cv_score)
        for k, v in test_metrics.items():
            mlflow.log_metric(f"test_{k}", v)

        _log_plots(best, X_te, y_te, plots_root / name)
        mlflow.sklearn.log_model(best, artifact_path="model")
        LOGGER.info("[%s] cv_roc_auc=%.4f  test_metrics=%s", name, cv_score, test_metrics)

    return best, {"cv_roc_auc": cv_score, **test_metrics}


def main() -> int:
    df = pd.read_csv(DATA_PATH)
    X, y = split_features_target(df)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    mlflow.set_tracking_uri(MLFLOW_DIR.as_uri())
    mlflow.set_experiment(EXPERIMENT_NAME)
    plots_root = ROOT / "reports" / "figures"

    with mlflow.start_run(run_name="parent"):
        mlflow.log_param("n_features", len(ALL_FEATURES))
        mlflow.log_param("n_train", len(X_tr))
        mlflow.log_param("n_test", len(X_te))

        lr_model, lr_metrics = _train_one(
            "logistic_regression",
            LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
            {"model__C": [0.1, 1.0, 10.0], "model__penalty": ["l2"]},
            X_tr, y_tr, X_te, y_te, cv, plots_root,
        )
        rf_model, rf_metrics = _train_one(
            "random_forest",
            RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
            {
                "model__n_estimators": [200, 400],
                "model__max_depth": [None, 6, 10],
                "model__min_samples_split": [2, 5],
            },
            X_tr, y_tr, X_te, y_te, cv, plots_root,
        )

        # Per assignment instruction the production model is Random Forest.
        # Logistic Regression is still trained, evaluated and logged as the
        # required second baseline for comparison.
        candidates = {"logistic_regression": (lr_model, lr_metrics),
                      "random_forest": (rf_model, rf_metrics)}
        best_name = "random_forest"
        best_model, best_metrics = candidates[best_name]
        mlflow.log_param("selected_model", best_name)
        for k, v in best_metrics.items():
            mlflow.log_metric(f"selected_{k}", v)

        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with MODEL_PATH.open("wb") as f:
            pickle.dump(best_model, f)
        mlflow.log_artifact(str(MODEL_PATH), artifact_path="serving")
        LOGGER.info("Saved best model (%s) -> %s", best_name, MODEL_PATH)

        summary = {
            "selected_model": best_name,
            "metrics": {
                "logistic_regression": lr_metrics,
                "random_forest": rf_metrics,
            },
        }
        METRICS_PATH.write_text(json.dumps(summary, indent=2))
        mlflow.log_artifact(str(METRICS_PATH))
        LOGGER.info("Wrote metrics summary -> %s", METRICS_PATH)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
