import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

os.makedirs("reports/visuals", exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 11, "figure.autolayout": True})

print("==================================================")
print("1. LOADING PROCESSED DATASET")
print("==================================================")
df = pd.read_csv("data/processed/railway_transit_processed.csv", low_memory=False)
print(f"Loaded {len(df):,} processed records.")

print("\n==================================================")
print("2. HYPOTHESIS TESTING (STATION BOTTLENECK ANALYSIS)")
print("==================================================")
# Define top 5 high-density hub junctions vs regular stations
top_hubs = df["station_name"].value_counts().head(5).index.tolist()
hub_halts = df[df["station_name"].isin(top_hubs)]["halt_time_min"]
regular_halts = df[~df["station_name"].isin(top_hubs)]["halt_time_min"]

# Perform Mann-Whitney U test (non-parametric two-sample test for skewed dwell times)
u_stat, p_val = stats.mannwhitneyu(hub_halts, regular_halts, alternative="two-sided")
print(f"Top 5 Hubs Mean Halt: {hub_halts.mean():.2f} min (Std: {hub_halts.std():.2f})")
print(f"Regular Stations Mean Halt: {regular_halts.mean():.2f} min (Std: {regular_halts.std():.2f})")
print(f"Mann-Whitney U Statistic: {u_stat:,.1f}, p-value: {p_val:.4e}")

if p_val < 0.05:
    print("Result: Reject H0 -> Statistically significant difference in dwell times between major hubs and intermediate stops (p < 0.05).")
else:
    print("Result: Fail to reject H0 -> No significant difference detected.")

print("\n==================================================")
print("3. GENERATING PUBLICATION VISUALS")
print("==================================================")

# 1. Halt Time Distribution (Log Scale)
plt.figure(figsize=(9, 5))
sns.histplot(df[df["halt_time_min"] > 0]["halt_time_min"], bins=50, kde=True, color="#2b5c8f", log_scale=True)
plt.title("Transit Halt Duration Distribution (Log Scale)", fontsize=13, weight="bold")
plt.xlabel("Halt Duration (Minutes, Log Scale)")
plt.ylabel("Station Stop Frequency")
plt.savefig("reports/visuals/01_halt_time_distribution.png", dpi=300)
plt.close()
print("Saved: reports/visuals/01_halt_time_distribution.png")

# 2. Top 10 Most Congested Junctions
top_10_stations = df["station_name"].value_counts().head(10).reset_index()
top_10_stations.columns = ["station_name", "train_count"]

plt.figure(figsize=(10, 5.5))
sns.barplot(data=top_10_stations, x="train_count", y="station_name", palette="Blues_r")
plt.title("Top 10 Indian Railway Junctions by Scheduled Transit Volume", fontsize=13, weight="bold")
plt.xlabel("Number of Scheduled Train Transits")
plt.ylabel("Junction / Station Name")
plt.savefig("reports/visuals/02_top_junctions_congestion.png", dpi=300)
plt.close()
print("Saved: reports/visuals/02_top_junctions_congestion.png")

# 3. Isolation Forest Anomaly Detection Scatter
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df.sample(20000, random_state=42),
    x="segment_distance_km",
    y="halt_time_min",
    hue="is_anomaly",
    palette={0: "#4a90e2", 1: "#d0021b"},
    alpha=0.6,
    s=25
)
plt.title("Isolation Forest: Operational Transit Bottleneck Anomalies", fontsize=13, weight="bold")
plt.xlabel("Inter-Station Segment Distance (km)")
plt.ylabel("Halt Time at Station (min)")
plt.legend(title="Status", labels=["Anomaly", "Normal"])
plt.savefig("reports/visuals/03_isolation_forest_anomalies.png", dpi=300)
plt.close()
print("Saved: reports/visuals/03_isolation_forest_anomalies.png")

# 4. Boxplot of Segment Distances
plt.figure(figsize=(9, 4))
sns.boxplot(x=df["segment_distance_km"], color="#50e3c2", fliersize=2)
plt.title("Distribution of Inter-Station Transit Segment Distances", fontsize=13, weight="bold")
plt.xlabel("Segment Distance (km)")
plt.savefig("reports/visuals/04_segment_distance_boxplot.png", dpi=300)
plt.close()
print("Saved: reports/visuals/04_segment_distance_boxplot.png")

print("\nAll statistical visuals generated and saved under reports/visuals/!")
