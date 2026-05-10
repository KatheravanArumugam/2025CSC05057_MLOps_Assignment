# 4️⃣ Testing & Linting

Part of assignment task **5 — CI/CD & Automated Testing (8 marks)**.

## 4.1 Run all tests

```bash
source .venv/bin/activate
pytest -v
```

Expected: **14 passed** (4 preprocessing + 2 data-cleaning + 2 model + 5 API + 1 metrics endpoint).

Tests cover:

| File | What it checks |
|------|----------------|
| `tests/test_preprocessing.py` | Feature lists, NaN handling, determinism, missing-column rejection |
| `tests/test_data_download.py` | `?` → NaN, target binarisation, no input mutation |
| `tests/test_model.py` | Pickle loads, has `predict`/`predict_proba`, accepts canonical feature order |
| `tests/test_api.py` | `/`, `/health`, `/predict` shape, `422` validation, `/metrics` exposes counters |

Note: `test_model.py` and `test_api.py` are **skipped** if `models/heart_disease_model.pkl` is missing — train first.

## 4.2 Coverage report

```bash
pytest --cov=src --cov-report=term-missing --cov-report=xml:reports/coverage.xml
```

Open `reports/coverage.xml` (or use `--cov-report=html`) to inspect.

## 4.3 Lint

```bash
flake8 src tests
```

Configuration is in `.flake8` (max-line-length = 110, sensible ignores).

## 4.4 What Jenkins runs

The Jenkins `Lint`, `Unit tests`, and `Train model` stages execute exactly the commands above. JUnit XML and coverage are archived as build artefacts.

➡️ Next: [`05_api_local.md`](05_api_local.md).
