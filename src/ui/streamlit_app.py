"""Minimal Streamlit UI that calls the FastAPI /predict endpoint.

Run:
    streamlit run src/ui/streamlit_app.py
Then open http://localhost:8501.

The API base URL can be overridden via the HEART_API_URL env var, e.g.
    HEART_API_URL=http://localhost:18080 streamlit run src/ui/streamlit_app.py
"""
from __future__ import annotations

import os
from typing import Any, Dict

import requests
import streamlit as st

API_URL = os.environ.get("HEART_API_URL", "http://localhost:8000").rstrip("/")

CP_OPTIONS = {
    "Typical angina (0)": 0,
    "Atypical angina (1)": 1,
    "Non-anginal pain (2)": 2,
    "Asymptomatic (3)": 3,
}
RESTECG_OPTIONS = {
    "Normal (0)": 0,
    "ST-T wave abnormality (1)": 1,
    "Left ventricular hypertrophy (2)": 2,
}
SLOPE_OPTIONS = {"Up-sloping (0)": 0, "Flat (1)": 1, "Down-sloping (2)": 2}
THAL_OPTIONS = {"Normal (3)": 3.0, "Fixed defect (6)": 6.0, "Reversible defect (7)": 7.0}
SEX_OPTIONS = {"Female (0)": 0, "Male (1)": 1}
YESNO = {"No (0)": 0, "Yes (1)": 1}


st.set_page_config(page_title="Heart Disease Risk Predictor", page_icon="❤️", layout="centered")
st.title("❤️ Heart Disease Risk Predictor")
st.caption(f"Front-end for the FastAPI service at `{API_URL}` — UCI Heart Disease model (Random Forest).")

with st.sidebar:
    st.subheader("Service status")
    try:
        h = requests.get(f"{API_URL}/health", timeout=2).json()
        st.success(f"API up — model {h.get('model_version', '?')}")
    except Exception as exc:  # noqa: BLE001
        st.error(f"API unreachable: {exc}")
    st.markdown(f"[OpenAPI docs]({API_URL}/docs)  ·  [Metrics]({API_URL}/metrics)")

st.markdown("Enter the 13 clinical features and click **Predict**.")

col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age (years)", min_value=1, max_value=120, value=63)
    sex = SEX_OPTIONS[st.selectbox("Sex", list(SEX_OPTIONS))]
    cp = CP_OPTIONS[st.selectbox("Chest pain type", list(CP_OPTIONS), index=3)]
    trestbps = st.number_input("Resting blood pressure (mm Hg)", min_value=50, max_value=250, value=145)
    chol = st.number_input("Serum cholesterol (mg/dl)", min_value=100, max_value=600, value=233)
    fbs = YESNO[st.selectbox("Fasting blood sugar > 120 mg/dl", list(YESNO), index=1)]
    restecg = RESTECG_OPTIONS[st.selectbox("Resting ECG", list(RESTECG_OPTIONS))]
with col2:
    thalach = st.number_input("Max heart rate achieved", min_value=60, max_value=220, value=150)
    exang = YESNO[st.selectbox("Exercise-induced angina", list(YESNO))]
    oldpeak = st.number_input("ST depression (oldpeak)", min_value=0.0, max_value=10.0, value=2.3, step=0.1)
    slope = SLOPE_OPTIONS[st.selectbox("ST-segment slope", list(SLOPE_OPTIONS))]
    ca = st.number_input("Major vessels coloured (0-4)", min_value=0, max_value=4, value=0)
    thal = THAL_OPTIONS[st.selectbox("Thalassemia", list(THAL_OPTIONS))]

payload: Dict[str, Any] = {
    "age": float(age), "sex": sex, "cp": cp, "trestbps": float(trestbps),
    "chol": float(chol), "fbs": fbs, "restecg": restecg, "thalach": float(thalach),
    "exang": exang, "oldpeak": float(oldpeak), "slope": slope,
    "ca": float(ca), "thal": float(thal),
}

with st.expander("Request JSON (sent to /predict)"):
    st.json(payload)

if st.button("🩺 Predict", type="primary", use_container_width=True):
    try:
        r = requests.post(f"{API_URL}/predict", json=payload, timeout=5)
        r.raise_for_status()
        result = r.json()
    except requests.HTTPError as exc:
        st.error(f"HTTP {exc.response.status_code}: {exc.response.text}")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Request failed: {exc}")
    else:
        label = result["label"]
        confidence = result["confidence"]
        prediction = result["prediction"]

        if prediction == 1:
            st.error(f"⚠️ **Heart disease likely** — confidence {confidence:.1%}")
        else:
            st.success(f"✅ **No heart disease detected** — confidence {confidence:.1%}")

        m1, m2, m3 = st.columns(3)
        m1.metric("Prediction", label)
        m2.metric("Confidence", f"{confidence:.3f}")
        m3.metric("Model version", result.get("model_version", "?"))

        st.progress(min(max(confidence, 0.0), 1.0))

        with st.expander("Raw response"):
            st.json(result)

st.divider()
st.caption(
    "This UI is a thin client over the FastAPI `/predict` endpoint — the model is loaded "
    "and served inside the API container, not duplicated here."
)
