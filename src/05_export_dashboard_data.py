import os
import pandas as pd
import numpy as np

print("==================================================")
print("1. LOADING PROCESSED DATASET")
print("==================================================")
df = pd.read_csv("data/processed/railway_transit_processed.csv", low_memory=False)
print(f"Loaded {len(df):,} processed records.")

os.makedirs("dashboard", exist_ok=True)

print("\n==================================================")
print("2. COMPUTING JUNCTION & CORRIDOR AGGREGATIONS")
print("==================================================")

# Table 1: Station Junction Performance
station_perf = df.groupby(["station_code", "station_name"]).agg(
    total_trains_handled=("train_no", "count"),
    avg_halt_min=("halt_time_min", "mean"),
    max_halt_min=("halt_time_min", "max"),
    total_anomalies=("is_anomaly", "sum")
).reset_index()

station_perf["anomaly_rate_pct"] = (station_perf["total_anomalies"] / station_perf["total_trains_handled"]) * 100
station_perf = station_perf.sort_values(by="total_trains_handled", ascending=False)

# Table 2: Route Corridor Performance
route_perf = df.groupby(["train_no", "train_name"]).agg(
    total_stops=("seq", "max"),
    total_distance_km=("distance", "max"),
    total_halt_duration_min=("halt_time_min", "sum"),
    anomaly_stops=("is_anomaly", "sum")
).reset_index()

route_perf["avg_segment_km"] = route_perf["total_distance_km"] / route_perf["total_stops"]
route_perf = route_perf.sort_values(by="total_distance_km", ascending=False)

print(f"Generated metrics for {len(station_perf):,} stations and {len(route_perf):,} unique train routes.")

print("\n==================================================")
print("3. WHAT-IF SCENARIO: BOTTLENECK DWELL OPTIMIZATION")
print("==================================================")
# Evaluate cumulative daily hours saved across Indian Railways with halt time optimizations
total_baseline_halt_hrs = df["halt_time_min"].sum() / 60

scenarios = [
    {"Scenario": "Baseline", "Dwell Reduction %": "0%", "Total Dwell Hours": total_baseline_halt_hrs, "Daily Hours Saved": 0},
    {"Scenario": "Moderate Optimization", "Dwell Reduction %": "10%", "Total Dwell Hours": total_baseline_halt_hrs * 0.90, "Daily Hours Saved": total_baseline_halt_hrs * 0.10},
    {"Scenario": "Advanced Optimization", "Dwell Reduction %": "15%", "Total Dwell Hours": total_baseline_halt_hrs * 0.85, "Daily Hours Saved": total_baseline_halt_hrs * 0.15},
    {"Scenario": "Peak Smart-Signaling", "Dwell Reduction %": "20%", "Total Dwell Hours": total_baseline_halt_hrs * 0.80, "Daily Hours Saved": total_baseline_halt_hrs * 0.20}
]
scenario_df = pd.DataFrame(scenarios)
print(scenario_df.to_string(index=False))

print("\n==================================================")
print("4. EXPORTING DASHBOARD DATA TABLES")
print("==================================================")

station_perf.to_csv("dashboard/station_junction_performance.csv", index=False)
route_perf.to_csv("dashboard/corridor_route_performance.csv", index=False)
scenario_df.to_csv("dashboard/what_if_dwell_scenarios.csv", index=False)

with pd.ExcelWriter("dashboard/railway_transit_bi_pack.xlsx", engine="openpyxl") as writer:
    station_perf.head(250).to_excel(writer, sheet_name="Top_Stations", index=False)
    route_perf.head(250).to_excel(writer, sheet_name="Top_Routes", index=False)
    scenario_df.to_excel(writer, sheet_name="What_If_Model", index=False)

print("Exported:")
print(" - dashboard/station_junction_performance.csv")
print(" - dashboard/corridor_route_performance.csv")
print(" - dashboard/what_if_dwell_scenarios.csv")
print(" - dashboard/railway_transit_bi_pack.xlsx")
