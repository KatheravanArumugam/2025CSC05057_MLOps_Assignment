# 3️⃣ Feature Engineering, Training & MLflow

## 3.1 Preprocessing pipeline

`src/features/preprocessing.py` builds a single sklearn `ColumnTransformer`:

| Block | Columns | Steps |
|-------|---------|-------|
| Numeric | age, trestbps, chol, thalach, oldpeak, ca | `SimpleImputer(median)` → `StandardScaler` |
| Categorical | sex, cp, fbs, restecg, exang, slope, thal | `SimpleImputer(most_frequent)` → `OneHotEncoder(handle_unknown='ignore')` |

The same fitted transformer is bundled inside the final `Pipeline`, so training and serving cannot drift.

## 3.2 Train both models (LR + Random Forest)

```bash
source .venv/bin/activate
python -m src.models.train
```

Workflow:

1. 80/20 stratified train/test split (seed = 42).
2. `StratifiedKFold(n_splits=5)` cross-validation, `GridSearchCV` on `roc_auc`.
3. **Logistic Regression** grid: `C ∈ {0.1, 1, 10}`.
4. **Random Forest** grid: `n_estimators ∈ {200, 400}`, `max_depth ∈ {None, 6, 10}`, `min_samples_split ∈ {2, 5}`.
5. **Random Forest is selected as the production model** (per assignment instruction). Logistic Regression is logged in MLflow as the required baseline.
6. Saves `models/heart_disease_model.pkl` and `models/metrics.json`.
7. Logs everything to MLflow at `./mlruns/`.

### 3.2.1 Latest results obtained on this machine

| Model | CV ROC-AUC | Test Acc | Test Precision | Test Recall | Test F1 | Test ROC-AUC |
|-------|-----------:|---------:|---------------:|------------:|--------:|-------------:|
| Logistic Regression | 0.9113 | 0.8852 | 0.8387 | 0.9286 | 0.8814 | **0.9610** |
| Random Forest (selected) | 0.8976 | 0.9016 | 0.8438 | 0.9643 | 0.9000 | 0.9426 |

> RF wins on accuracy / F1 / recall; LR has a marginally higher ROC-AUC. Both are well within an acceptable production range.

## 3.3 Open the MLflow UI

```bash
source .venv/bin/activate
mlflow ui --backend-store-uri ./mlruns --port 5000
# open http://127.0.0.1:5000
```

Each run logs:
* Hyperparameters (`model_family`, `model__C`, `model__n_estimators`, …).
* Cross-validation ROC-AUC and 5 test metrics.
* Plots: confusion matrix, ROC curve.
* The fitted sklearn pipeline (`mlflow.sklearn.log_model`).
* The serving pickle (`heart_disease_model.pkl`) under the `serving/` artefact path of the parent run.

## 3.4 Reproducibility checklist

✅ Pinned `requirements.txt`.
✅ Single sklearn pipeline = preprocessing + model.
✅ Deterministic seed (`random_state=42`).
✅ Same pipeline is loaded by the API for inference (no manual re-implementation).
✅ Pickle saved + MLflow run ID recorded in `models/metrics.json`.

➡️ Next: [`04_testing_and_lint.md`](04_testing_and_lint.md).
