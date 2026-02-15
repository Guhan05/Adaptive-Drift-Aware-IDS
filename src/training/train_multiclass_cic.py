import os
import glob
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping


# =========================================================
# SAFE DATA LOADING (CHUNK-BASED FOR 8GB RAM)
# =========================================================

print("Loading dataset safely using chunk processing...")

csv_files = glob.glob("data/CICIDS2018/*.csv")

df_list = []

for file in csv_files:
    print("Processing:", file)

    chunk_iter = pd.read_csv(file, chunksize=50000)
    sampled_chunks = []

    for chunk in chunk_iter:

        chunk.columns = chunk.columns.str.strip()

        # Remove repeated header rows
        if "Dst Port" in chunk.columns:
            chunk = chunk[chunk["Dst Port"] != "Dst Port"]

        # Drop identifiers
        drop_cols = [
            "Flow ID",
            "Source IP",
            "Destination IP",
            "Timestamp"
        ]

        chunk = chunk.drop(
            columns=[c for c in drop_cols if c in chunk.columns],
            errors="ignore"
        )

        # Convert numeric safely
        for col in chunk.columns:
            if col != "Label":
                chunk[col] = pd.to_numeric(chunk[col], errors="coerce")

        chunk = chunk.replace([np.inf, -np.inf], np.nan)
        chunk = chunk.dropna()

        # Sample per chunk
        if len(chunk) > 10000:
            chunk = chunk.sample(n=10000, random_state=42)

        sampled_chunks.append(chunk)

    file_df = pd.concat(sampled_chunks, ignore_index=True)

    # Extra safety per file
    if len(file_df) > 80000:
        file_df = file_df.sample(n=80000, random_state=42)

    df_list.append(file_df)

df = pd.concat(df_list, ignore_index=True)

print("Initial dataset shape:", df.shape)


# =========================================================
# REMOVE ULTRA-RARE CLASSES (<100 samples)
# =========================================================

class_counts = df["Label"].value_counts()
valid_labels = class_counts[class_counts >= 100].index

df = df[df["Label"].isin(valid_labels)]

print("Dataset shape after removing rare classes:", df.shape)


# =========================================================
# LABEL ENCODING
# =========================================================

le = LabelEncoder()
df["Label"] = le.fit_transform(df["Label"])

num_classes = len(le.classes_)
print("Number of classes:", num_classes)
print("Classes:", le.classes_)


# =========================================================
# FEATURE SCALING (float32 safe)
# =========================================================

X = df.drop(columns=["Label"])
y = df["Label"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X).astype("float32")


# =========================================================
# TRAIN-TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Train shape:", X_train.shape)
print("Test shape:", X_test.shape)


# =========================================================
# CLASS WEIGHTING (CRITICAL FOR IMBALANCE)
# =========================================================

class_weights = compute_class_weight(
    class_weight="balanced",
    classes=np.unique(y_train),
    y=y_train
)

class_weights = dict(enumerate(class_weights))

print("Class Weights:", class_weights)


# =========================================================
# BUILD MULTI-CLASS ANN
# =========================================================

model = Sequential([
    Dense(256, activation='relu', input_shape=(X_train.shape[1],)),
    Dropout(0.3),

    Dense(128, activation='relu'),
    Dropout(0.3),

    Dense(64, activation='relu'),

    Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("\nTraining Multi-Class Model...\n")

early_stop = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

history = model.fit(
    X_train,
    y_train,
    validation_split=0.2,
    epochs=50,
    batch_size=512,
    callbacks=[early_stop],
    class_weight=class_weights,
    verbose=1
)


# =========================================================
# EVALUATION
# =========================================================

print("\nEvaluating Model...\n")

loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print("Test Accuracy:", accuracy)

y_pred_probs = model.predict(X_test)
y_pred = np.argmax(y_pred_probs, axis=1)

print("\nClassification Report:\n")
print(classification_report(
    y_test,
    y_pred,
    target_names=le.classes_,
    zero_division=0
))

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))


# =========================================================
# SAVE MODEL (NEW KERAS FORMAT)
# =========================================================

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(BASE, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "multiclass_ids_model.keras")
model.save(MODEL_PATH)

print("\nMulti-Class Model Saved Successfully!")
