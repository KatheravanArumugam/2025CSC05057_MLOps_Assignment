# 9️⃣ Monitoring & Logging

## 9.1 What the API exposes

| Type | Where | Detail |
|------|-------|--------|
| Structured logs | stdout | JSON-style line per request, includes `pred`, `confidence`, `model_version` |
| Prometheus metrics | `GET /metrics` | Default HTTP metrics from `prometheus-fastapi-instrumentator` **plus** custom: `heart_disease_predictions_total{prediction=...}`, `heart_disease_prediction_latency_seconds_*` |

## 9.2 Local stack (Docker Compose)

```bash
docker compose -f deployment/docker-compose.yml up --build
```

* **Prometheus** at http://localhost:9090
  * Status → Targets → `heart-disease-api` should be `UP`.
  * Try the query: `sum by (prediction)(rate(heart_disease_predictions_total[1m]))`.
* **Grafana** at http://localhost:3000 (login `admin/admin`)
  * The dashboard `Heart Disease API` is auto-provisioned. It has 5 panels:
    1. Total predictions (stat)
    2. Predictions / sec (stat)
    3. Predictions by class (timeseries)
    4. `/predict` p95 latency (timeseries)
    5. HTTP request rate by handler/status

Generate some traffic to populate the panels:

```bash
for i in $(seq 1 100); do
  curl -s -X POST http://localhost:8000/predict -H 'Content-Type: application/json' \
    -d '{"age":63,"sex":1,"cp":3,"trestbps":145,"chol":233,"fbs":1,"restecg":0,
         "thalach":150,"exang":0,"oldpeak":2.3,"slope":0,"ca":0,"thal":1}' > /dev/null
done
```

## 9.3 Kubernetes stack

If you installed kube-prometheus-stack:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
kubectl apply -f deployment/k8s/50-servicemonitor.yaml
```

Then port-forward:

```bash
kubectl -n monitoring port-forward svc/kube-prometheus-grafana 3000:80
# admin / prom-operator
```

Re-import `monitoring/grafana/heart_disease_dashboard.json` (Dashboards → Import → Upload).

➡️ Next: [`10_post_deployment_verification.md`](10_post_deployment_verification.md).
