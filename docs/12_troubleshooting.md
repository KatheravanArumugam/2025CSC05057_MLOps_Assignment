# 🛠️ Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `RuntimeError: Model file not found at .../heart_disease_model.pkl` (API startup) | Model never trained | `python -m src.models.train` |
| `ModuleNotFoundError: src` when running `python src/...` | Run as a module, not a path | Use `python -m src.module.name` |
| `pytest` skips `test_model.py` and `test_api.py` | No model artefact yet | Train the model, then re-run pytest |
| `urllib3 NotOpenSSLWarning` | Bundled `ssl` is LibreSSL on macOS Python 3.9 | Cosmetic; safe to ignore. Or upgrade to Python 3.11+. |
| `docker info` says daemon not running | Docker Desktop not started | Open Docker Desktop, wait for the whale icon |
| `docker build` fails copying `models/` | You haven't trained yet | `python -m src.models.train` first |
| `kubectl ... ImagePullBackOff` on Minikube | Image is on host daemon, not Minikube's | `eval $(minikube docker-env)` then re-build |
| Prometheus target shows `DOWN` | Service name / port mismatch | Confirm `monitoring/prometheus.yml` targets `api:8000` (Compose) or correct service in k8s |
| Grafana panels are empty | No traffic yet | Run the curl loop in `docs/09_monitoring.md` |
| Jenkins fails at `Setup Python` | `python3` not on agent PATH | Install Python 3.11 on the agent or use a Docker agent (`agent { docker { image 'python:3.11-slim' } }`) |
| `mlflow ui` opens but no runs | Wrong working directory | Run from the repo root so the relative `./mlruns` matches |
| `flake8` fails on long lines | Forgot to keep ≤ 110 chars | Either reformat or extend `.flake8` |
| API container exits immediately, no logs | Health-check Python missing tools | Inspect with `docker logs heart-disease-api` — usually the model file isn't baked into the image |

## Quick reset

```bash
rm -rf .venv mlruns models/heart_disease_model.pkl reports/figures
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.data.download_data
python -m src.data.eda
python -m src.models.train
pytest -v
```
