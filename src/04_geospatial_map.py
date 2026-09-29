import os
import pandas as pd
import folium

print("==================================================")
print("1. LOADING PROCESSED DATA & PREPARING GEO-MASTER")
print("==================================================")

df = pd.read_csv("data/processed/railway_transit_processed.csv", low_memory=False)

# Master coordinates mapped via standardized Station Code (IR standard)
station_coords = {
    "CSMT": (18.9400, 72.8354, "Chhatrapati Shivaji Maharaj Terminus"),
    "KYN":  (19.2361, 73.1306, "Kalyan Junction"),
    "TNA":  (19.1860, 72.9759, "Thane"),
    "SDAH": (22.5667, 88.3716, "Sealdah"),
    "MSB":  (13.0970, 80.2936, "Chennai Beach"),
    "HWH":  (22.5850, 88.3468, "Howrah Junction"),
    "DR":   (19.0178, 72.8478, "Dadar"),
    "DDJ":  (22.6214, 88.3934, "Dum Dum Junction"),
    "CLA":  (19.0657, 72.8793, "Kurla"),
    "TBM":  (12.9249, 80.1200, "Tambaram"),
    "BZA":  (16.5186, 80.6199, "Vijayawada Junction"),
    "PNVL": (18.9894, 73.1175, "Panvel"),
    "CNB":  (26.4547, 80.3507, "Kanpur Central"),
    "BRC":  (22.3107, 73.1812, "Vadodara Junction"),
    "NDLS": (28.6139, 77.2090, "New Delhi"),
    "PNBE": (25.5941, 85.1376, "Patna Junction"),
    "ADI":  (23.0225, 72.5714, "Ahmedabad Junction"),
    "GWL":  (26.2183, 78.1828, "Gwalior Junction"),
    "BPL":  (23.2599, 77.4126, "Bhopal Junction"),
    "SBC":  (12.9716, 77.5946, "KSR Bengaluru"),
    "LKO":  (26.8306, 80.9234, "Lucknow Charbagh"),
    "PUNE": (18.5284, 73.8744, "Pune Junction"),
    "NGP":  (21.1524, 79.0888, "Nagpur Junction"),
    "JP":   (26.9196, 75.7878, "Jaipur Junction"),
    "PRYJ": (25.4358, 81.8463, "Prayagraj Junction")
}

# Aggregate volume and mean dwell duration by station code
station_agg = df.groupby(["station_code", "station_name"]).agg(
    total_trains=("train_no", "count"),
    avg_halt=("halt_time_min", "mean"),
    anomalies=("is_anomaly", "sum")
).reset_index()

# Map coordinates by station code
station_agg["coords"] = station_agg["station_code"].map(lambda x: station_coords.get(x, None))
mapped_stations = station_agg.dropna(subset=["coords"]).copy()

mapped_stations["lat"] = mapped_stations["coords"].apply(lambda x: x[0])
mapped_stations["lon"] = mapped_stations["coords"].apply(lambda x: x[1])
mapped_stations["full_name"] = mapped_stations["coords"].apply(lambda x: x[2])

print(f"Mapped {len(mapped_stations)} strategic railway junctions across India.")

print("\n==================================================")
print("2. RENDERING INTERACTIVE FOLIUM MAP")
print("==================================================")

# Standard OpenStreetMap tile (no API token required)
india_map = folium.Map(location=[21.7679, 78.8718], zoom_start=5, tiles="OpenStreetMap")

for _, row in mapped_stations.iterrows():
    radius = max(6, min(22, row["total_trains"] / 50))
    color = "#d0021b" if row["anomalies"] > 15 else "#1f77b4"
    
    popup_text = f"""
    <div style='font-family: Arial, sans-serif; font-size: 12px; width: 190px;'>
        <h4 style='margin: 0 0 5px 0; color: #0d3b66;'>{row['full_name']}</h4>
        <b>Station Code:</b> {row['station_code']}<br>
        <b>Total Transits:</b> {row['total_trains']:,}<br>
        <b>Avg Halt:</b> {row['avg_halt']:.2f} min<br>
        <b>Detected Anomalies:</b> <span style='color:red;'>{int(row['anomalies'])}</span>
    </div>
    """
    
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=radius,
        popup=folium.Popup(popup_text, max_width=250),
        tooltip=f"{row['full_name']} ({row['total_trains']} trains)",
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        weight=2
    ).add_to(india_map)

output_map_path = "reports/interactive_transit_map.html"
india_map.save(output_map_path)
print(f"Interactive Folium map saved to: {output_map_path}")
