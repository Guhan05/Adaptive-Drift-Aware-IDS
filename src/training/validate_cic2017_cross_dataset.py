import os
import glob
import json
import numpy as np
import pandas as pd
import joblib

from sklearn.metrics import classification_report, confusion_matrix, roc_curve
from tensorflow.keras.models import load_model

# =========================================================
# CONFIGURATION
# =========================================================

TARGET_FPR = 0.05   # Enterprise target: <= 5% false positive rate

print("\n=== ENTERPRISE CROSS-DATASET VALIDATION ===\n")

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(BASE, "models")

# =========================================================
# LOAD TRAINED MODELS
# =========================================================

print("Loading trained models...\n")

ann_model = load_model(os.path.join(MODEL_DIR, "adaptive_binary_ann_model.keras"))
iso_model = joblib.load(os.path.join(MODEL_DIR, "iso_model.pkl"))
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
feature_columns = joblib.load(os.path.join(MODEL_DIR, "feature_columns.pkl"))

# =========================================================
# LOAD CICIDS2017 PARQUET FILES
# =========================================================

print("Loading CICIDS2017 dataset...\n")

parquet_files = glob.glob("data/**/*.parquet", recursive=True)
df_list = []

for file in parquet_files:
    print("Processing:", file)

    df = pd.read_parquet(file)
    df.columns = df.columns.str.strip()

    # Rename 2017 columns to match 2018 format
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

    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0

    df = df[feature_columns + ["Label"]]

    for col in feature_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    df_list.append(df)

df = pd.concat(df_list, ignore_index=True)

print("Dataset shape:", df.shape)

# =========================================================
# LABEL PROCESSING
# =========================================================

df["Label"] = df["Label"].apply(lambda x: 0 if x == "Benign" else 1)

X = df.drop(columns=["Label"])
y = df["Label"]

X_scaled = scaler.transform(X).astype("float32")

# =========================================================
# HYBRID RISK SCORE COMPUTATION
# =========================================================

print("\nComputing enterprise risk scores...\n")

ann_probs = ann_model.predict(X_scaled, verbose=0).flatten()

iso_scores = iso_model.decision_function(X_scaled)
iso_scores = (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min())
iso_probs = 1 - iso_scores

ann_conf = np.abs(ann_probs - 0.5) * 2

hybrid_scores = []
prev_score = 0.5

for ann_p, iso_p, conf in zip(ann_probs, iso_probs, ann_conf):

    w_ann = 0.4 + 0.5 * (conf ** 1.5)
    w_ann = min(max(w_ann, 0.1), 0.9)
    w_iso = 1 - w_ann

    score = (w_ann * ann_p) + (w_iso * iso_p)

    # Temporal smoothing
    score = 0.7 * score + 0.3 * prev_score
    prev_score = score

    hybrid_scores.append(score)

hybrid_scores = np.array(hybrid_scores)

risk_scores = hybrid_scores * 100

# =========================================================
# THRESHOLD SELECTION BASED ON FPR
# =========================================================

print("\nSelecting threshold based on FPR <= 5%...\n")

fpr, tpr, thresholds = roc_curve(y, hybrid_scores)

selected_threshold = 0.5

for i in range(len(fpr)):
    if fpr[i] <= TARGET_FPR:
        selected_threshold = thresholds[i]
        break

print(f"Selected threshold: {selected_threshold:.4f}")

final_preds = (hybrid_scores >= selected_threshold).astype(int)

# =========================================================
# RESULTS
# =========================================================

print("\n=== ENTERPRISE RESULTS (FPR Controlled) ===\n")

print(classification_report(y, final_preds))
print("Confusion Matrix:")
print(confusion_matrix(y, final_preds))

fp_rate = confusion_matrix(y, final_preds)[0][1] / sum(y == 0)

print(f"\nFalse Positive Rate: {fp_rate:.4f}")
print(f"Alert Rate: {np.mean(final_preds):.4f}")
