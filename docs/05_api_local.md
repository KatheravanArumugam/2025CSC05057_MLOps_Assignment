# 5️⃣ Running the API locally

## 5.1 Start it

```bash
source .venv/bin/activate
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

Open http://127.0.0.1:8000/docs for interactive Swagger UI.

## 5.2 Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Service info |
| GET | `/health` | 200 once model is loaded |
| POST | `/predict` | JSON in → prediction + confidence |
| GET | `/metrics` | Prometheus exposition format |
| GET | `/docs` | Swagger UI |

## 5.3 Sample request

```bash
curl -s -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age":63,"sex":1,"cp":3,"trestbps":145,"chol":233,
       "fbs":1,"restecg":0,"thalach":150,"exang":0,
       "oldpeak":2.3,"slope":0,"ca":0,"thal":1}' | jq .
```

Expected response shape:

```json
{
  "prediction": 0,
  "label": "no_disease",
  "confidence": 0.59,
  "probabilities": [0.59, 0.41],
  "model_version": "v1"
}
```

> Smoke-test executed during initial setup returned `pred=0 confidence=0.5938` for the sample above.

## 5.4 Schema validation

Send an incomplete payload to confirm 422:

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" -d '{"age":63}'
# -> 422
```

➡️ Next: [`06_docker.md`](06_docker.md).
