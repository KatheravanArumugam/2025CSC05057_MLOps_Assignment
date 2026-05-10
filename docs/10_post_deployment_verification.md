# 🔟 Post-Deployment Verification (after **you** deploy)

This is your end-to-end smoke-test once you have:

1. Run the Jenkins pipeline successfully on `main`.
2. Applied the Kubernetes manifests.
3. Started the monitoring stack.

## 10.1 Checklist

- [ ] `kubectl -n mlops get pods` shows **2/2 Running**, no `CrashLoopBackOff`.
- [ ] `kubectl -n mlops logs deploy/heart-disease-api` shows `Model loaded from /app/models/heart_disease_model.pkl`.
- [ ] `GET /health` returns `200` with `{"status":"ok"}`.
- [ ] `POST /predict` with the sample payload returns a JSON body with `prediction`, `label`, `confidence`, `probabilities`, `model_version`.
- [ ] `GET /metrics` returns Prometheus exposition text including `heart_disease_predictions_total`.
- [ ] Prometheus → Targets shows `heart-disease-api` UP.
- [ ] Grafana panels populate after sending a few requests.

## 10.2 Useful commands

```bash
# Pod status
kubectl -n mlops get pods,svc -o wide

# Tail API logs
kubectl -n mlops logs -f deploy/heart-disease-api

# Run a load burst
URL=$(minikube service heart-disease-api -n mlops --url)   # or http://localhost
for i in $(seq 1 200); do
  curl -s -X POST $URL/predict -H 'Content-Type: application/json' \
    -d '{"age":63,"sex":1,"cp":3,"trestbps":145,"chol":233,"fbs":1,"restecg":0,
         "thalach":150,"exang":0,"oldpeak":2.3,"slope":0,"ca":0,"thal":1}' >/dev/null
done

# Confirm metrics counted them
kubectl -n mlops port-forward svc/heart-disease-api 8000:80 &
curl -s http://127.0.0.1:8000/metrics | grep heart_disease_predictions_total
```

## 10.3 Document in the final report

After verification, update `reports/final_report.md` with:

* The exact Jenkins build number that succeeded (e.g. `#42`).
* The image tag deployed (e.g. `heart-disease-api:42`).
* Real numbers from `models/metrics.json`.
* Embeds of the screenshots you captured.

➡️ Next: [`11_screenshot_and_video_checklist.md`](11_screenshot_and_video_checklist.md).
