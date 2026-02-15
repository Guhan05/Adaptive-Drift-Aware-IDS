import os
import glob
import numpy as np
import pandas as pd
import joblib

from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.models import load_model

# =========================================================
# LOAD TRAINED 2018 OBJECTS
# =========================================================

print("Loading trained 2018 models...")

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(BASE, "models")

ann_model = load_model(os.path.join(MODEL_DIR, "adaptive_binary_ann_model.keras"))
iso_model = joblib.load(os.path.join(MODEL_DIR, "iso_model.pkl"))
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
feature_columns = joblib.load(os.path.join(MODEL_DIR, "feature_columns.pkl"))

# =========================================================
# LOAD CICIDS2017 PARQUET FILES
# =========================================================

print("Loading CICIDS2017 Parquet dataset...")

parquet_files = glob.glob("data/**/*.parquet", recursive=True)

df_list = []

for file in parquet_files:
    print("Processing:", file)

    df = pd.read_parquet(file)
    df.columns = df.columns.str.strip()

    # Column mapping (2017 → 2018 format)
    rename_map = {
        "Total Fwd Packets": "Tot Fwd Pkts",
        "Total Backward Packets": "Tot Bwd Pkts",
        "Fwd Packets Length Total": "TotLen Fwd Pkts",
        "Bwd Packets Length Total": "TotLen Bwd Pkts",
        "Fwd Packet Length Max": "Fwd Pkt Len Max",
        "Fwd Packet Length Min": "Fwd Pkt Len Min",
        "Fwd Packet Length Mean": "Fwd Pkt Len Mean",
        "Fwd Packet Length Std": "Fwd Pkt Len Std",
        "Bwd Packet Length Max": "Bwd Pkt Len Max",
        "Bwd Packet Length Min": "Bwd Pkt Len Min",
        "Bwd Packet Length Mean": "Bwd Pkt Len Mean",
        "Bwd Packet Length Std": "Bwd Pkt Len Std",
        "Flow Bytes/s": "Flow Byts/s",
        "Flow Packets/s": "Flow Pkts/s",
        "Fwd IAT Total": "Fwd IAT Tot",
        "Bwd IAT Total": "Bwd IAT Tot",
        "Fwd Header Length": "Fwd Header Len",
        "Bwd Header Length": "Bwd Header Len",
        "Fwd Packets/s": "Fwd Pkts/s",
        "Bwd Packets/s": "Bwd Pkts/s",
        "Packet Length Min": "Pkt Len Min",
        "Packet Length Max": "Pkt Len Max",
        "Packet Length Mean": "Pkt Len Mean",
        "Packet Length Std": "Pkt Len Std",
        "Packet Length Variance": "Pkt Len Var",
        "FIN Flag Count": "FIN Flag Cnt",
        "SYN Flag Count": "SYN Flag Cnt",
        "RST Flag Count": "RST Flag Cnt",
        "PSH Flag Count": "PSH Flag Cnt",
        "ACK Flag Count": "ACK Flag Cnt",
        "URG Flag Count": "URG Flag Cnt",
        "ECE Flag Count": "ECE Flag Cnt",
        "Avg Packet Size": "Pkt Size Avg",
        "Avg Fwd Segment Size": "Fwd Seg Size Avg",
        "Avg Bwd Segment Size": "Bwd Seg Size Avg",
        "Subflow Fwd Packets": "Subflow Fwd Pkts",
        "Subflow Fwd Bytes": "Subflow Fwd Byts",
        "Subflow Bwd Packets": "Subflow Bwd Pkts",
        "Subflow Bwd Bytes": "Subflow Bwd Byts",
        "Init Fwd Win Bytes": "Init Fwd Win Byts",
        "Init Bwd Win Bytes": "Init Bwd Win Byts",
        "Fwd Act Data Packets": "Fwd Act Data Pkts"
    }

    df = df.rename(columns=rename_map)

    required_cols = feature_columns + ["Label"]
    df = df[[col for col in required_cols if col in df.columns]]

    for col in feature_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    df_list.append(df)

df = pd.concat(df_list, ignore_index=True)

print("2017 dataset shape:", df.shape)

# =========================================================
# BINARY LABEL
# =========================================================

df["Label"] = df["Label"].apply(lambda x: 0 if x == "Benign" else 1)

X = df.drop(columns=["Label"])
y = df["Label"]

for col in feature_columns:
    if col not in X.columns:
        X[col] = 0

X = X[feature_columns]

X_scaled = scaler.transform(X).astype("float32")

# =========================================================
# HYBRID COMPUTATION (IMPROVED)
# =========================================================

print("\nComputing improved hybrid probabilities...\n")

ann_probs = ann_model.predict(X_scaled, verbose=0).flatten()

iso_scores = iso_model.decision_function(X_scaled)
iso_scores = (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min())
iso_probs = 1 - iso_scores

ann_conf = np.abs(ann_probs - 0.5) * 2

adaptive_scores = []
previous_score = 0.5  # initial neutral

for ann_p, iso_p, conf in zip(ann_probs, iso_probs, ann_conf):

    # Nonlinear confidence scaling
    w_ann = 0.4 + 0.5 * (conf ** 1.5)
    w_ann = min(max(w_ann, 0.1), 0.9)
    w_iso = 1 - w_ann

    hybrid_score = (w_ann * ann_p) + (w_iso * iso_p)

    # Temporal smoothing
    smoothed_score = (0.7 * hybrid_score) + (0.3 * previous_score)
    previous_score = smoothed_score

    adaptive_scores.append(smoothed_score)

adaptive_scores = np.array(adaptive_scores)

# =========================================================
# CONFIDENCE-AWARE DYNAMIC THRESHOLD
# =========================================================

final_preds = []

for score, conf in zip(adaptive_scores, ann_conf):

    dynamic_threshold = 0.5 - (0.1 * (1 - conf))
    pred = 1 if score > dynamic_threshold else 0
    final_preds.append(pred)

final_preds = np.array(final_preds)

# =========================================================
# RESULTS
# =========================================================

print("\nIMPROVED HYBRID CROSS DATASET RESULTS (2018 → 2017)\n")
print(classification_report(y, final_preds))
print(confusion_matrix(y, final_preds))
