# 🚆 Railway Transit & Bottleneck Resilience Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Isolation%20Forest-orange.svg)](https://scikit-learn.org/)
[![Sweetviz](https://img.shields.io/badge/EDA-Sweetviz%20Automated-green.svg)](https://pypi.org/project/sweetviz/)
[![Folium](https://img.shields.io/badge/Geospatial-Folium%20Leaflet-red.svg)](https://python-visualization.github.io/folium/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end data engineering, machine learning anomaly detection, and operational intelligence pipeline analyzing **186,114** schedule transitions across the Indian Railways network. Developed for 5th-Semester Project-Based Learning (PBL) in Data Science & Analytics (CSE0521).

---

## 📌 Project Overview

Transit delays, disproportionate station dwell times, and junction bottlenecks across dense rail corridors generate severe supply-chain ripple effects and commuter congestion. This project implements a scalable analytical architecture to ingest raw transit logs, engineer inter-station dynamics, isolate operational anomalies using unsupervised machine learning, evaluate spatial traffic density across India's rail network, and project delay reduction scenarios.

### 🎯 Sustainable Development Goals (SDGs)
* **SDG 9: Industry, Innovation, and Infrastructure** — Fostering resilient transport infrastructure and data-driven schedule optimization.
* **SDG 8: Decent Work and Economic Growth** — Mitigating logistics transit dead-time and operational delay costs.

---

## 🏗️ Architecture & Pipeline Flow

+-------------------------------+
|   Raw Schedule Data (CSV)     |  (186,124 raw records from Kaggle)
+---------------+---------------+
|
v
+-------------------------------+
| Unit 2: Ingestion & Sweetviz  |  (Null audits, distribution profiling, HTML export)
+---------------+---------------+
|
v
+-------------------------------+
| Unit 3: Wrangling & Cleaning  |  (Corrupted row filtering, timestamp sanitization,
|                               |   Origin/Terminus zero-handling, 24-hr modulo)
+---------------+---------------+
|
v
+-------------------------------+
| Unit 3: Feature Engineering   |  (halt_time_min, segment_distance_km,
|                               |   inter-station transition gaps)
+---------------+---------------+
|
v
+-------------------------------+
| Unit 3: ML Anomaly Detection  |  (Isolation Forest: contamination=0.015,
|                               |   2,792 extreme bottlenecks isolated)
+---------------+---------------+
|
v
+-------------------------------+
| Unit 3: Hypothesis Testing    |  (Mann-Whitney U: Hub Dwell vs. Waypoints, p < 0.001)
+---------------+---------------+
|
v
+-------------------------------+
| Unit 4: Geospatial Analytics  |  (Folium OpenStreetMap: 24 strategic junction hubs,
|                               |   traffic density bubble scaling & anomaly tooltips)
+---------------+---------------+
|
v
+-------------------------------+
| Unit 5: BI & What-If Modeling |  (Multi-sheet Excel pack, 10%-20% dwell reduction models,
|                               |   Power BI / Tableau ready aggregations)
+-------------------------------+

## 📊 Dataset Specifications

* **Primary Source:** Indian Railways Time Table Dataset (Nilesh Kadam)
* **Raw Records:** 186,124 rows across 12 raw attributes
* **Sanitized Records Retained:** 186,114 rows (10 corrupted/shifted-delimiter rows filtered)
* **Coverage:** 11,112 unique trains | 8,147 unique stations

### Key Engineered Schema
| Field Name | Type | Description |
| :--- | :--- | :--- |
| `train_no` | `string` | Normalized train identifier code |
| `station_code` | `string` | Standardized 3-to-4 letter Indian Railways station code |
| `seq` | `integer` | Monotonically increasing station stop sequence index |
| `halt_time_min` | `float` | Dwell duration (adjusted for midnight transitions & terminus zeros) |
| `segment_distance_km` | `float` | Incremental distance traversed from preceding stop |
| `is_anomaly` | `integer` | Binary label (1: Operational Bottleneck, 0: Nominal) |
| `anomaly_score` | `float` | Raw Isolation Forest decision function score |

---

## 🚀 Key Empirical Insights & Results

* **Top Hub Volumes:** CST Mumbai (1,027 transits), Kalyan Jn (828), Thane (796), Sealdah (745), and Chennai Beach (738) form the highest density transit bottlenecks in India.
* **Anomaly Footprint:** Isolation Forest isolated **2,792 extreme anomalies (1.50%)** marked by prolonged dwell durations (>45 min) or disproportionate inter-station transit ratios.
* **Sensitivity / What-If Projection:**
  * **Moderate Optimization (10% dwell cut):** **689.76 daily operational hours** saved network-wide.
  * **Target Optimization (15% dwell cut):** **1,034.64 daily operational hours** saved.
  * **Peak Smart-Signaling (20% dwell cut):** **1,379.52 daily operational hours** saved.

---

## 💻 Repository Directory Structure

```text
railway-transit-analytics/
├── .gitignore                          # Excludes raw data caches & virtual environments
├── README.md                           # Formal project specification & execution docs
├── requirements.txt                    # Exact pinned dependencies
├── src/                                # Modular pipeline source scripts
│   ├── 01_profile_data.py              # Sweetviz automated exploratory profiling
│   ├── 02_clean_and_engineer.py        # Cleaning, transit feature engineering, Isolation Forest
│   ├── 03_statistical_eda.py           # Mann-Whitney U testing & publication visual generation
│   ├── 04_geospatial_map.py            # Folium interactive geospatial map rendering
│   └── 05_export_dashboard_data.py     # BI aggregations & What-If scenario modeling
├── reports/                            # Generated analytics deliverables
│   ├── sweetviz_raw_data_profile.html  # Unit 2: Sweetviz HTML profiling report
│   ├── interactive_transit_map.html    # Unit 4: Interactive Folium Leaflet map
│   └── visuals/                        # Unit 3: High-res publication plots
│       ├── 01_halt_time_distribution.png
│       ├── 02_top_junctions_congestion.png
│       ├── 03_isolation_forest_anomalies.png
│       └── 04_segment_distance_boxplot.png
└── dashboard/                          # Production-ready BI data tables
    ├── station_junction_performance.csv
    ├── corridor_route_performance.csv
    ├── what_if_dwell_scenarios.csv
    └── railway_transit_bi_pack.xlsx

    ⚙️ Installation & Replication
1. Clone & Set Up Environment
Bash
git clone [https://github.com/agrawalsanskar-max/railway-transit-analytics.git](https://github.com/agrawalsanskar-max/railway-transit-analytics.git)
cd railway-transit-analytics

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

2. Execute Data Pipeline Sequentially
Bash
# Unit 2: Run automated profiling
python src/01_profile_data.py

# Unit 3: Run wrangling, feature engineering, and ML anomaly detection
python src/02_clean_and_engineer.py

# Unit 3: Run statistical hypothesis testing & plot publication figures
python src/03_statistical_eda.py

# Unit 4: Generate interactive geospatial map
python src/04_geospatial_map.py

# Unit 5: Export BI reporting tables & what-if sensitivity models
python src/05_export_dashboard_data.py

👥 Contributors & Academic Context
Author: Sanskar Agrawal

Institution: ITM University Gwalior

Course: B.Tech Computer Science & Engineering (Semester V)

Subject: Data Science & Analytics (CSE0521)

Once that completes, stage and push the changes:

```powershell
git add README.md reports/
git commit -m "docs: add full architecture README and generated report assets"
git push origin main