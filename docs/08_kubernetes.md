# 8️⃣ Kubernetes Deployment (Task 7, 7 marks)

## 8.1 Pick a cluster

Choose **one** of these — they are equivalent for the assignment:

### Option A — Docker Desktop's Kubernetes (easiest on macOS)

1. Open Docker Desktop → Settings → **Kubernetes** → enable.
2. Wait until the green status appears.
3. `kubectl config current-context` should print `docker-desktop`.

### Option B — Minikube

```bash
brew install minikube
minikube start --cpus=2 --memory=4g --driver=docker
eval $(minikube -p minikube docker-env)   # makes kubectl/minikube use the same daemon
```

## 8.2 Build the image *into the cluster's docker daemon*

```bash
# Docker Desktop K8s already shares the host daemon — just build:
docker build -f deployment/Dockerfile -t heart-disease-api:latest .

# Minikube:
eval $(minikube -p minikube docker-env)
docker build -f deployment/Dockerfile -t heart-disease-api:latest .
```

## 8.3 Apply the manifests

```bash
kubectl apply -f deployment/k8s/00-namespace.yaml
kubectl apply -f deployment/k8s/10-configmap.yaml
kubectl apply -f deployment/k8s/20-deployment.yaml
kubectl apply -f deployment/k8s/30-service.yaml

# Optional:
kubectl apply -f deployment/k8s/40-ingress.yaml         # if an ingress controller is installed
kubectl apply -f deployment/k8s/50-servicemonitor.yaml  # if kube-prometheus-stack is installed
```

Or in one shot:

```bash
kubectl apply -f deployment/k8s/
```

## 8.4 Verify

```bash
kubectl -n mlops get pods -w        # wait for 2/2 Running
kubectl -n mlops get svc            # note the EXTERNAL-IP / NodePort
kubectl -n mlops describe deployment/heart-disease-api
```

### Hit the service

* **Docker Desktop:** `EXTERNAL-IP` will be `localhost`. Use `http://localhost/health`.
* **Minikube:** `minikube service heart-disease-api -n mlops --url`
* Universal port-forward fallback:

```bash
kubectl -n mlops port-forward svc/heart-disease-api 8000:80
curl -s http://127.0.0.1:8000/health
```

Send a prediction:

```bash
curl -s -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"age":63,"sex":1,"cp":3,"trestbps":145,"chol":233,"fbs":1,
       "restecg":0,"thalach":150,"exang":0,"oldpeak":2.3,"slope":0,"ca":0,"thal":1}'
```

## 8.5 What is in each manifest

| File | Resource | Notes |
|------|----------|-------|
| `00-namespace.yaml` | Namespace `mlops` | Isolates the workload |
| `10-configmap.yaml` | ConfigMap `heart-disease-config` | `LOG_LEVEL`, `MODEL_VERSION` |
| `20-deployment.yaml` | Deployment, 2 replicas, RollingUpdate, readiness/liveness probes, CPU/mem limits, Prometheus annotations |
| `30-service.yaml` | Service type `LoadBalancer` exposing port 80 → 8000 |
| `40-ingress.yaml` | Optional NGINX Ingress on `heart-disease.local` |
| `50-servicemonitor.yaml` | Optional, requires the kube-prometheus-stack CRDs |

## 8.6 What to capture for grading

* `kubectl -n mlops get pods,svc` output → `screenshots/k8s_resources.png`.
* Browser hitting `/docs` through the LoadBalancer / port-forward → `screenshots/k8s_swagger.png`.
* A successful `/predict` call screenshot → `screenshots/k8s_predict.png`.

➡️ Next: [`09_monitoring.md`](09_monitoring.md).
