import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

print("==================================================")
print("1. DATA WRANGLING & TYPE SANITIZATION")
print("==================================================")

file_path = "data/raw/railway_transit_raw.csv"
df = pd.read_csv(file_path, low_memory=False)
raw_count = len(df)
print(f"Initial raw record count: {raw_count:,}")

# Standardize column headers
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Drop corrupted rows where numeric sequence or distance cannot be converted
df["seq"] = pd.to_numeric(df["seq"], errors="coerce")
df["distance"] = pd.to_numeric(df["distance"], errors="coerce")
df = df.dropna(subset=["seq", "distance", "arrival_time", "departure_time"]).copy()

df["seq"] = df["seq"].astype(int)
df["distance"] = df["distance"].astype(int)
df["train_no"] = df["train_no"].astype(str).str.strip("'\" ")
df["station_code"] = df["station_code"].astype(str).str.strip().str.upper()
df["station_name"] = df["station_name"].astype(str).str.strip().str.title()

print(f"Valid records retained: {len(df):,} (Filtered out {raw_count - len(df)} corrupted rows)")

print("\n==================================================")
print("2. FEATURE ENGINEERING (TRANSIT DYNAMICS)")
print("==================================================")

# Convert string timestamps to minutes from midnight
def parse_time_to_minutes(time_series):
    parts = time_series.str.split(":", expand=True)
    hours = pd.to_numeric(parts[0], errors="coerce").fillna(0)
    minutes = pd.to_numeric(parts[1], errors="coerce").fillna(0)
    return hours * 60 + minutes

df["arr_min"] = parse_time_to_minutes(df["arrival_time"])
df["dep_min"] = parse_time_to_minutes(df["departure_time"])

# Dwell / Halt time calculation (handling midnight transitions)
# For origin stations (arr=0:00:00) and terminus stations (dep=0:00:00), halt is set to 0
is_origin_or_terminus = (df["arrival_time"] == "0:00:00") | (df["departure_time"] == "0:00:00")
halt = df["dep_min"] - df["arr_min"]
halt = np.where(halt < 0, halt + 1440, halt)  # Crossed midnight
df["halt_time_min"] = np.where(is_origin_or_terminus, 0, halt)

# Sort by train and sequence to compute inter-station segment metrics
df = df.sort_values(by=["train_no", "seq"]).reset_index(drop=True)

# Segment distance from previous station
df["prev_distance"] = df.groupby("train_no")["distance"].shift(1).fillna(0)
df["segment_distance_km"] = df["distance"] - df["prev_distance"]
df["segment_distance_km"] = df["segment_distance_km"].clip(lower=0)

print(f"Halt duration summary (minutes):")
print(df["halt_time_min"].describe())

print("\n==================================================")
print("3. AI ANOMALY DETECTION (ISOLATION FOREST)")
print("==================================================")
# Target halt times and segment distances to detect network bottlenecks and scheduling anomalies
features = df[["halt_time_min", "segment_distance_km"]].fillna(0)

iso_forest = IsolationForest(
    n_estimators=100,
    contamination=0.015,  # Flag top 1.5% extreme operational outliers
    random_state=42,
    n_jobs=-1
)
preds = iso_forest.fit_predict(features)
df["is_anomaly"] = np.where(preds == -1, 1, 0)
df["anomaly_score"] = iso_forest.decision_function(features)

anomaly_count = df["is_anomaly"].sum()
print(f"Total operational anomalies flagged: {anomaly_count:,} ({anomaly_count / len(df) * 100:.2f}%)")

# Export clean, production-grade dataset
os.makedirs("data/processed", exist_ok=True)
clean_csv_path = "data/processed/railway_transit_processed.csv"
df.to_csv(clean_csv_path, index=False)
print(f"\nProcessed dataset exported successfully to: {clean_csv_path}")
