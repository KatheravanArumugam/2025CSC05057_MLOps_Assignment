# 1️⃣ Local Setup

## 1.1 Prerequisites

| Tool | Version (tested) | Install (macOS) |
|------|------------------|-----------------|
| Python | 3.9 – 3.11 | `brew install python@3.11` |
| Git | 2.x | already installed on macOS |
| Docker Desktop | 24+ | https://www.docker.com/products/docker-desktop |
| (optional) Minikube | 1.33+ | `brew install minikube` |
| (optional) `kubectl` | 1.28+ | `brew install kubectl` |
| (optional) Java 17 (for Jenkins) | 17 | `brew install openjdk@17` |

> Already-detected on this machine: `python3 3.9.6`, `git`, `docker` CLI, `java`, `pdftotext`. The Docker **daemon** is not running yet — start Docker Desktop before doing the container/k8s steps.

## 1.2 Clone & enter the repo

```bash
cd ~/Documents/Python/ML_OPS_Assignment
```

## 1.3 Create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> ✅ This was already executed during initial setup. To re-create the venv from scratch later, just run the same block.

## 1.4 Verify

```bash
python -c "import sklearn, mlflow, fastapi, pandas; print('OK')"
```

You should see `OK`.

## 1.5 Project layout that is already on disk

```
ML_OPS_Assignment/
├── data/{raw,processed}
├── notebooks/
├── src/{data,features,models,api}
├── tests/
├── models/                # trained pickle goes here
├── mlruns/                # MLflow tracking store
├── deployment/{Dockerfile,docker-compose.yml,k8s/}
├── monitoring/{prometheus.yml, grafana/}
├── ci_cd/                 # reserved for any CI helpers
├── docs/                  # ⇽ you are here
├── reports/               # final report + figure outputs
├── screenshots/           # drop your screenshots here
├── requirements.txt
├── pytest.ini  .flake8  .gitignore  .dockerignore
├── Jenkinsfile
└── README.md
```

➡️ Continue to [`02_data_and_eda.md`](02_data_and_eda.md).
