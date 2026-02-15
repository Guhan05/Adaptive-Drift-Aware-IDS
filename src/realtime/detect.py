import numpy as np
import os
from tensorflow.keras.models import load_model
from sklearn.ensemble import IsolationForest
from .drift_controller import DriftController

EXPECTED_FEATURES = 77

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(BASE, "models", "ids_model.h5")

ann_model = load_model(MODEL_PATH)

iforest = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

iforest_fitted = False
drift_controller = DriftController()


def fit_iforest(X_normal):
    global iforest_fitted
    iforest.fit(X_normal)
    iforest_fitted = True


def build_feature_vector(features_dict):
    feature_vector = np.array(
        list(features_dict.values()),
        dtype=np.float32
    )

    if len(feature_vector) < EXPECTED_FEATURES:
        feature_vector = np.pad(
            feature_vector,
            (0, EXPECTED_FEATURES - len(feature_vector)),
            mode='constant'
        )

    if len(feature_vector) > EXPECTED_FEATURES:
        feature_vector = feature_vector[:EXPECTED_FEATURES]

    return feature_vector.reshape(1, -1)


def predict(features_dict, drift_score=0.0):

    drift_controller.update(drift_score)

    x = build_feature_vector(features_dict)

    ann_prob = float(ann_model.predict(x, verbose=0)[0][0])
    ann_prob = max(0.0, min(1.0, ann_prob))

    if iforest_fitted:
        iso_raw = float(iforest.decision_function(x)[0])
        iso_norm = (iso_raw + 1) / 2
        iso_norm = max(0.0, min(1.0, iso_norm))
    else:
        iso_norm = 0.5

    # 🔥 Dynamic Drift-Based Weighting
    w_ann, w_anom = drift_controller.get_weights()

    hybrid_score = w_ann * ann_prob + w_anom * (1 - iso_norm)
    hybrid_score = max(0.0, min(1.0, hybrid_score))

    risk_score = round(hybrid_score * 100, 2)

    if risk_score < 40:
        risk_level = "LOW"
    elif risk_score < 70:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    confidence = round(abs(risk_score - 50) * 2, 2)
    confidence = max(0.0, min(100.0, confidence))

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "confidence": confidence,
        "prediction": 1 if risk_level != "LOW" else 0,
        "mode": drift_controller.mode
    }
