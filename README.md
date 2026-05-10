# Heart Disease MLOps — End-to-End Project

[![python](https://img.shields.io/badge/python-3.11-blue)]() [![framework](https://img.shields.io/badge/api-FastAPI-009688)]() [![tracking](https://img.shields.io/badge/tracking-MLflow-0194E2)]() [![ci](https://img.shields.io/badge/ci-Jenkins-D33833)]() [![deploy](https://img.shields.io/badge/deploy-Kubernetes-326CE5)]()

End-to-end MLOps implementation for the **MLOps Assignment-I (S2-25_AMLCSZG523)**.
Trains a **Random Forest** classifier on the UCI Heart Disease dataset and ships it as a containerised, monitored, Kubernetes-deployable FastAPI service with a Jenkins CI/CD pipeline.

> ⚠️ **All step-by-step instructions live in [`docs/`](docs/00_overview.md)** — start there.

## Quickstart

```bash
# 1. Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Data + EDA
python -m src.data.download_data
python -m src.data.eda

# 3. Train (LR + RF, RF selected) + MLflow
python -m src.models.train
mlflow ui --backend-store-uri ./mlruns --port 5000   # http://127.0.0.1:5000

# 4. Tests + lint
pytest -v
flake8 src tests

# 5. Local API
uvicorn src.api.app:app --reload                     # http://127.0.0.1:8000/docs

# 6. Docker (start Docker Desktop first)
docker build -f deployment/Dockerfile -t heart-disease-api:latest .
docker run --rm -p 8000:8000 heart-disease-api:latest

# 7. Local stack (API + Prometheus + Grafana)
docker compose -f deployment/docker-compose.yml up --build

# 8. Kubernetes (Docker Desktop or Minikube)
kubectl apply -f deployment/k8s/
```

Sample request:

```bash
curl -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d '{
  "age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233, "fbs": 1,
  "restecg": 0, "thalach": 150, "exang": 0, "oldpeak": 2.3,
  "slope": 0, "ca": 0, "thal": 1
}'
```

Sample response:

```json
{"prediction": 0, "label": "no_disease", "confidence": 0.59,
 "probabilities": [0.59, 0.41], "model_version": "v1"}
```

## Coverage of assignment tasks

| # | Task | Marks | Where it lives |
|---|------|------:|----------------|
| 1 | Data Acquisition & EDA | 5 | `src/data/download_data.py`, `src/data/eda.py`, `notebooks/01_EDA.ipynb` |
| 2 | Feature Engineering & Models (LR + RF) | 8 | `src/features/preprocessing.py`, `src/models/train.py` |
| 3 | Experiment Tracking (MLflow) | 5 | `mlruns/` + tracking calls in `train.py` |
| 4 | Model Packaging & Reproducibility | 7 | `models/heart_disease_model.pkl`, `requirements.txt`, sklearn `Pipeline` |
| 5 | CI/CD & Automated Tests | 8 | `Jenkinsfile`, `tests/`, `.flake8`, `pytest.ini` |
| 6 | Containerization | 5 | `deployment/Dockerfile`, `deployment/docker-compose.yml` |
| 7 | Production Deployment | 7 | `deployment/k8s/*.yaml` |
| 8 | Monitoring & Logging | 3 | `monitoring/`, `/metrics`, structured JSON logs |
| 9 | Documentation & Reporting | 2 | `docs/`, `reports/final_report.md` |

## Latest results (random_state=42)

| Model | CV ROC-AUC | Test Acc | Test Precision | Test Recall | Test F1 | Test ROC-AUC |
|-------|-----------:|---------:|---------------:|------------:|--------:|-------------:|
| Logistic Regression | 0.9113 | 0.8852 | 0.8387 | 0.9286 | 0.8814 | 0.9610 |
| **Random Forest (selected)** | **0.8976** | **0.9016** | **0.8438** | **0.9643** | **0.9000** | **0.9426** |

## Repository structure

See [`docs/00_overview.md`](docs/00_overview.md) for the full tour.

## License

Educational use — BITS Pilani MLOps S2-25_AMLCSZG523.
