# 📸 Screenshot & 🎥 Video Checklist

The assignment asks for a **screenshots folder** and a **short video** of the end-to-end pipeline (deliverables a/b).

## 11.1 Screenshots to capture (drop into `screenshots/`)

| # | Filename suggestion | What to show |
|---|---------------------|--------------|
| 1 | `01_eda_class_balance.png` | Output of `python -m src.data.eda` or notebook cell with the class balance plot |
| 2 | `02_eda_correlation.png` | Correlation heatmap |
| 3 | `03_mlflow_runs.png` | MLflow UI listing both runs side-by-side with metrics |
| 4 | `04_mlflow_run_detail.png` | One run's params + metrics + artifacts (incl. confusion matrix) |
| 5 | `05_pytest_pass.png` | Terminal showing `14 passed` |
| 6 | `06_flake8_clean.png` | Empty flake8 output |
| 7 | `07_docker_build.png` | `docker build` final `Successfully tagged heart-disease-api:latest` |
| 8 | `08_docker_run_predict.png` | `curl /predict` against the local container |
| 9 | `09_jenkins_pipeline.png` | Stage view, all stages green |
| 10 | `10_jenkins_artifacts.png` | Build artifacts list (model.pkl, metrics.json) |
| 11 | `11_k8s_resources.png` | `kubectl get pods,svc -n mlops` |
| 12 | `12_k8s_swagger.png` | `/docs` via the cluster URL |
| 13 | `13_k8s_predict.png` | `curl /predict` via the cluster URL |
| 14 | `14_prometheus_targets.png` | Targets page, `heart-disease-api` UP |
| 15 | `15_grafana_dashboard.png` | Populated Grafana dashboard |
| 16 | `16_api_logs.png` | Pod logs showing structured prediction JSON |

> All filenames are suggestions — what matters is that each item from the table is visible somewhere in the report.

## 11.2 Video script (≈ 5 minutes)

Recommended order (mirrors the docs):

1. **Repo tour** (15 s) — show folder structure in your editor.
2. **Data + EDA** (30 s) — run `python -m src.data.download_data` then `python -m src.data.eda`, open one figure.
3. **Training + MLflow** (60 s) — run `python -m src.models.train`, then `mlflow ui` and walk through the runs.
4. **Tests + lint** (30 s) — `pytest -v` + `flake8 src tests`.
5. **API local** (30 s) — `uvicorn …`, hit `/docs`, do a `/predict`.
6. **Docker** (30 s) — `docker build`, `docker run`, `curl` again.
7. **Jenkins** (45 s) — show "Build Now", stage view going green, archived artifacts.
8. **Kubernetes** (45 s) — `kubectl apply -f deployment/k8s/`, `kubectl get pods`, hit the LoadBalancer.
9. **Monitoring** (30 s) — Prometheus targets, Grafana dashboard with traffic.
10. **Wrap-up** (15 s) — summarise metrics from `models/metrics.json`.

Recommended tools (macOS): **QuickTime Player → File → New Screen Recording**, or `cmd+shift+5`. For voice + screen, OBS Studio works well.

## 11.3 Where to drop everything

```
screenshots/        ← PNGs above
reports/            ← final_report.md (plus exported PDF)
videos/             ← create this when you record (not under git for size reasons)
```
