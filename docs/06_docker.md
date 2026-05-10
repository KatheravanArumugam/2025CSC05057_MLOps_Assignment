# 6️⃣ Docker — Containerization (Task 6, 5 marks)

## 6.1 Pre-flight

* Docker Desktop must be **running** (you can verify with `docker info`).
* You must have a freshly trained model: run `python -m src.models.train` first if `models/heart_disease_model.pkl` does not exist.

## 6.2 Build the image

From the repo root:

```bash
docker build -f deployment/Dockerfile -t heart-disease-api:latest .
```

The Dockerfile is multi-stage:

| Stage | What happens |
|-------|--------------|
| `builder` | Builds wheels for all pinned dependencies in `/wheels` |
| runtime | `python:3.11-slim`, copies wheels + source + model, drops to a non-root user, exposes 8000, defines a `HEALTHCHECK`, runs `uvicorn src.api.app:app` |

## 6.3 Run the container

```bash
docker run --rm -p 8000:8000 --name heart-disease-api heart-disease-api:latest
```

In another terminal:

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' \
  -d '{"age":63,"sex":1,"cp":3,"trestbps":145,"chol":233,"fbs":1,"restecg":0,
       "thalach":150,"exang":0,"oldpeak":2.3,"slope":0,"ca":0,"thal":1}'
```

## 6.4 Run with monitoring (Compose)

```bash
docker compose -f deployment/docker-compose.yml up --build
```

Services:

| Service | URL | Notes |
|---------|-----|-------|
| API | http://localhost:8000 | Swagger at `/docs` |
| Prometheus | http://localhost:9090 | Targets page should show `heart-disease-api` UP |
| Grafana | http://localhost:3000 | Login `admin` / `admin`, dashboard auto-provisioned |

To stop:

```bash
docker compose -f deployment/docker-compose.yml down
```

## 6.5 Tagging & pushing to a registry (optional)

```bash
docker tag heart-disease-api:latest <your-dockerhub-user>/heart-disease-api:latest
docker login
docker push <your-dockerhub-user>/heart-disease-api:latest
```

> The Jenkins pipeline does this automatically when `REGISTRY` env var is set and the `dockerhub-creds` credential exists.

➡️ Next: [`07_jenkins.md`](07_jenkins.md).
