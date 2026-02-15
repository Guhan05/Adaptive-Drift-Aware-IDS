import pandas as pd
import os


def load_replay_data(limit=5000):

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

    DATA_PATH = os.path.join(PROJECT_ROOT, "data")

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data folder not found at {DATA_PATH}")

    dataset_files = []

    for root, dirs, files in os.walk(DATA_PATH):
        for file in files:
            if file.lower().endswith(".csv") or file.lower().endswith(".parquet"):
                dataset_files.append(os.path.join(root, file))

    if not dataset_files:
        raise FileNotFoundError("No CSV or Parquet files found in data folder")

    file_path = dataset_files[0]

    print(f"Loading replay dataset: {file_path}")

    if file_path.lower().endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_parquet(file_path)

    for col in df.columns:
        if "label" in col.lower():
            df = df.drop(columns=[col])
            break

    df = df.fillna(0)
    df = df.iloc[:limit]

    print(f"Loaded {len(df)} rows")

    return df
