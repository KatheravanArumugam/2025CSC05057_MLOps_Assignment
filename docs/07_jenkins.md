# 7️⃣ Jenkins CI/CD

## 7.1 Install Jenkins (macOS, fastest path)

### Option A — Homebrew (recommended)

```bash
brew install jenkins-lts
brew services start jenkins-lts
# Default URL: http://localhost:8080
```

The first-run admin password is in:

```bash
cat ~/.jenkins/secrets/initialAdminPassword
```

### Option B — Docker (if you prefer not to install Java/Jenkins on your host)

```bash
docker run --name jenkins -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts-jdk17
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

> Mounting the docker socket lets the pipeline build images on your host's daemon.

## 7.2 First-run wizard

1. Open http://localhost:8080 → paste the unlock token.
2. Choose **Install suggested plugins**.
3. Create your admin user.

Add these plugins (Manage Jenkins → Plugins → Available):
* **Pipeline**, **Git**, **Docker Pipeline**, **Credentials Binding**, **JUnit**, **AnsiColor**, **Timestamper**.

## 7.3 Create the pipeline job

1. Dashboard → **New Item** → name `heart-disease-mlops` → **Multibranch Pipeline** (or **Pipeline**).
2. **Branch Sources / Source code management** → Git → URL of this repo, credentials if needed.
3. **Build configuration** → "by Jenkinsfile" → script path: `Jenkinsfile` (the file at the repo root).
4. Save → **Scan Multibranch Pipeline Now** (or "Build Now" for a Pipeline job).

## 7.4 Pipeline stages (`Jenkinsfile`)

| # | Stage | What it does | Always runs? |
|---|-------|--------------|--------------|
| 1 | Checkout | Clones the branch | ✅ |
| 2 | Setup Python | venv + `pip install -r requirements.txt` | ✅ |
| 3 | Lint | `flake8 src tests` | ✅ |
| 4 | Download data | `python -m src.data.download_data` | ✅ |
| 5 | Unit tests | `pytest --junitxml=reports/junit.xml --cov=src` | ✅ |
| 6 | Train model | `python -m src.models.train`, archives `models/*.pkl` and `mlruns/**` | ✅ |
| 7 | Build Docker image | `docker build -f deployment/Dockerfile` | only on `main` |
| 8 | Push image | `docker push` to `${REGISTRY}` | only on `main` AND `REGISTRY` set |
| 9 | Deploy to k8s | `kubectl apply -f deployment/k8s/` + rollout | only on `main` |

The pipeline **fails** if lint, tests, or training error out (Production-Readiness requirement: pipeline must fail on errors with clear logs).

## 7.5 Required Jenkins credentials

| ID | Type | Purpose |
|----|------|---------|
| `dockerhub-creds` | Username/Password | `docker login` for image push |
| `kubeconfig-cred` | Secret file | `kubeconfig` used by `kubectl` in the deploy stage |

Add these via **Manage Jenkins → Credentials → System → Global**.

➡️ Next: [`08_kubernetes.md`](08_kubernetes.md).
