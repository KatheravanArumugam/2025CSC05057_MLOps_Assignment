# 2️⃣ Data Acquisition & EDA

## 2.1 Download the dataset

```bash
source .venv/bin/activate
python -m src.data.download_data
```

This script:
1. Calls `ucimlrepo.fetch_ucirepo(id=45)` (UCI Heart Disease).
2. Falls back to a direct CSV mirror if the package call fails.
3. Saves:
   * `data/raw/heart_disease_raw.csv` — exact response from the source.
   * `data/processed/heart_disease.csv` — `?` markers → NaN, `num` binarised to a `target` column.

Expected output:

```
Saved raw   -> data/raw/heart_disease_raw.csv  (shape=(303, 14))
Saved clean -> data/processed/heart_disease.csv (shape=(303, 14))
Class balance:
target
0    164
1    139
```

## 2.2 Run EDA (script form — fast, no Jupyter needed)

```bash
python -m src.data.eda
```

Generates 5 figures into `reports/figures/eda/`:
* `class_balance.png`
* `histograms.png` — numeric features by target
* `correlation_heatmap.png`
* `categorical_vs_target.png`
* `missing_values.png` (only if missing values exist)

## 2.3 Run EDA (notebook form — interactive)

```bash
source .venv/bin/activate
jupyter notebook notebooks/01_EDA.ipynb
```

The notebook re-creates the same plots interactively, then ends with a "Key takeaways" markdown cell — extend it with your own observations if desired.

## 2.4 What to put in your report (suggested)

* Dataset shape: 303 × 14, target binarised.
* Class balance: `0 → 164`, `1 → 139` (≈ 54% / 46%, mildly imbalanced — accuracy is acceptable as a headline metric, but ROC-AUC is also reported).
* Missing values: a small handful in `ca` and `thal`; handled by median / most-frequent imputation in the preprocessing pipeline.
* Strongest visual class separation: `cp` (chest-pain type), `thalach` (max heart rate), `oldpeak`.

➡️ Next: [`03_training_and_mlflow.md`](03_training_and_mlflow.md).
