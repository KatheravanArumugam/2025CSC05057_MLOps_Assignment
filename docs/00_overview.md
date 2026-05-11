# 📘 Heart Disease MLOps — Project Overview

> **Dataset:** UCI Heart Disease (Cleveland) — 303 rows, 13 features, binary `target`
> **Production model:** Random Forest (Logistic Regression trained as baseline)

---

## 1. Architecture at a glance

```
                      ┌────────────────────────┐
                      │  UCI Heart Disease     │
                      │  Repository (id=45)    │
                      └──────────┬─────────────┘
                                 │ download_data.py
                                 ▼
        ┌────────────────────────────────────────────┐
        │   data/raw  →  data/processed/heart_*.csv  │
        └──────────┬─────────────────────────────────┘
                   │  EDA notebook + figures
                   ▼
        ┌────────────────────────────────────────────┐
        │  src/features/preprocessing.py (pipeline)  │
        │  src/models/train.py  →  GridSearchCV      │
        │     ├── Logistic Regression                │
        │     └── Random Forest  (selected)          │
        │  MLflow logs (mlruns/) + model.pkl         │
        └──────────┬─────────────────────────────────┘
                   │ pickle artefact
                   ▼
        ┌────────────────────────────────────────────┐
        │  src/api/app.py — FastAPI                  │
        │  /predict  /health  /metrics  /docs        │
        └──────────┬─────────────────────────────────┘
                   │ Dockerfile
                   ▼
        ┌────────────────────────────────────────────┐
        │  Jenkins pipeline (Jenkinsfile)            │
        │  lint → test → train → build → push → k8s  │
        └──────────┬─────────────────────────────────┘
                   ▼
        ┌────────────────────────────────────────────┐
        │  Kubernetes (deployment/k8s/*.yaml)        │
        │  + Prometheus + Grafana monitoring         │
        └────────────────────────────────────────────┘
```

## 2. Repository tour

| Path | Purpose |
|------|---------|
| `src/data/download_data.py` | Fetches the UCI dataset and produces a clean CSV |
| `src/data/eda.py` | Generates EDA figures into `reports/figures/eda/` |
| `src/features/preprocessing.py` | sklearn `ColumnTransformer` (impute + scale + one-hot) |
| `src/models/train.py` | Trains LR + RF, logs MLflow runs, saves best model as pickle |
| `src/api/app.py` + `schemas.py` | FastAPI service with `/predict`, `/health`, `/metrics` |
| `tests/` | pytest unit + API tests |
| `deployment/Dockerfile` | Multi-stage image for the API |
| `deployment/docker-compose.yml` | Local API + Prometheus + Grafana stack |
| `deployment/k8s/*.yaml` | Namespace, ConfigMap, Deployment, Service, Ingress, ServiceMonitor |
| `monitoring/` | Prometheus scrape config + Grafana provisioning |
| `Jenkinsfile` | Multi-stage CI/CD pipeline |
| `notebooks/01_EDA.ipynb` | Interactive EDA notebook |
| `reports/` | Final report (Markdown) and figure outputs |
| `docs/` | This step-by-step documentation |

## 3. Reading order

1. [`01_setup.md`](01_setup.md) — local environment (you are here once this is done)
2. [`02_data_and_eda.md`](02_data_and_eda.md) — data download + EDA
3. [`03_training_and_mlflow.md`](03_training_and_mlflow.md) — training, MLflow tracking
4. [`04_testing_and_lint.md`](04_testing_and_lint.md) — pytest + flake8
5. [`05_api_local.md`](05_api_local.md) — running the FastAPI service locally
6. [`06_docker.md`](06_docker.md) — building & running the Docker image
7. [`07_jenkins.md`](07_jenkins.md) — installing & running Jenkins, configuring the pipeline
8. [`08_kubernetes.md`](08_kubernetes.md) — deploying to Minikube / Docker-Desktop
9. [`09_monitoring.md`](09_monitoring.md) — Prometheus + Grafana
10. [`10_post_deployment_verification.md`](10_post_deployment_verification.md) — what to do **after** you deploy
11. [`12_troubleshooting.md`](12_troubleshooting.md) — common problems & fixes
