#!/usr/bin/env python3
"""
Railway Transit Analytics - Streamlit Interactive Operations Dashboard
B.Tech Project-Based Learning (CSE0521) - Data Science & Analytics
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 1. PAGE CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(
    page_title="Railway Transit Analytics | Operations Dashboard",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise-grade CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0d3b66 0%, #001f3f 100%);
        padding: 24px 30px;
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #f4d06f;
    }
    .main-header p {
        margin: 6px 0 0 0;
        font-size: 1.05rem;
        opacity: 0.9;
        color: #e0e6ed;
    }
    
    .kpi-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border-left: 5px solid #0d3b66;
        transition: transform 0.2s ease;
    }
    .kpi-container:hover {
        transform: translateY(-2px);
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748b;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 4px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.05rem;
        font-weight: 600;
        padding: 12px 24px;
        border-radius: 8px 8px 0 0;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. DATA INGESTION & CACHING WITH ERROR HANDLING
# ==============================================================================
DATA_EXCEL_PATH = os.path.join("dashboard", "railway_transit_bi_pack.xlsx")
GEO_MAP_PATH = os.path.join("reports", "interactive_transit_map.html")
BASELINE_DAILY_HOURS = 6897.60


@st.cache_data(show_spinner="Loading transit operations intelligence data...")
def load_data(file_path: str):
    """Load sheets from the consolidated BI Excel package with graceful fallbacks."""
    if not os.path.isfile(file_path):
        return None, None, None, f"Data file not found at '{file_path}'"

    try:
        xl = pd.ExcelFile(file_path, engine="openpyxl")
        required_sheets = ["Top_Stations", "Top_Routes", "What_If_Model"]
        missing_sheets = [s for s in required_sheets if s not in xl.sheet_names]
        if missing_sheets:
            return None, None, None, f"Missing required sheets: {', '.join(missing_sheets)}"

        df_stations = xl.parse("Top_Stations")
        df_routes = xl.parse("Top_Routes")
        df_what_if = xl.parse("What_If_Model")
        return df_stations, df_routes, df_what_if, None
    except Exception as e:
        return None, None, None, f"Error reading Excel package: {str(e)}"


# Header Banner
st.markdown("""
<div class="main-header">
    <h1>🚆 Indian Railways Transit Intelligence Platform</h1>
    <p>B.Tech PBL CSE0521 • Operational Congestion, ML Anomaly Profiling & Dwell Optimization</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Controls & Information
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/4/45/Indian_Railways_logo.svg", width=110)
    st.title("Operations Hub")
    st.markdown("""
    **Project Scope:**
    - Enterprise Big-Data Transit Analytics
    - Machine Learning Anomaly Detection (Isolation Forest)
    - Mann-Whitney U Bottleneck Significance Testing
    - Smart-Signaling What-If Simulation
    """)
    st.markdown("---")
    st.info("💡 **Pipeline Status**: Production-Ready\nData Source: `railway_transit_bi_pack.xlsx`")
    if st.button("🔄 Refresh Data Cache"):
        st.cache_data.clear()
        st.rerun()

# Load Data
df_stations, df_routes, df_what_if, error_msg = load_data(DATA_EXCEL_PATH)

if error_msg:
    st.error(f"❌ **Data Ingestion Error:** {error_msg}")
    st.warning("Please ensure you have executed the data pipeline orchestrator: `python main.py`")
    st.stop()


# ==============================================================================
# 3. TOP SUMMARY KPI CARDS
# ==============================================================================
# Required KPIs:
# - Corridors Evaluated (count of routes)
# - High-Volume Hubs Evaluated (count of stations)
# - Bottlenecks Flagged (sum of total_anomalies)
# - Network Average Dwell (mean of avg_halt_min, formatted to 2 decimals)

total_corridors = len(df_routes)
total_hubs = len(df_stations)
total_bottlenecks = int(df_stations["total_anomalies"].sum())
network_avg_dwell = df_stations["avg_halt_min"].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-container" style="border-left-color: #2b5c8f;">
        <div class="kpi-title">Corridors Evaluated</div>
        <div class="kpi-value">{total_corridors:,}</div>
        <div class="kpi-subtext">Active Route Schedules Analyzed</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-container" style="border-left-color: #0d9488;">
        <div class="kpi-title">High-Volume Hubs Evaluated</div>
        <div class="kpi-value">{total_hubs:,}</div>
        <div class="kpi-subtext">Strategic Junction Stations</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-container" style="border-left-color: #e11d48;">
        <div class="kpi-title">Bottlenecks Flagged</div>
        <div class="kpi-value">{total_bottlenecks:,}</div>
        <div class="kpi-subtext">Isolation Forest ML Anomalies</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-container" style="border-left-color: #f59e0b;">
        <div class="kpi-title">Network Average Dwell</div>
        <div class="kpi-value">{network_avg_dwell:.2f} <span style="font-size: 1rem; font-weight: 500;">min</span></div>
        <div class="kpi-subtext">Scheduled Junction Halt Mean</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")


# ==============================================================================
# 4. THREE INTERACTIVE TABS
# ==============================================================================
tab_congestion, tab_what_if, tab_geo = st.tabs([
    "📊 Operational Congestion",
    "🎯 Interactive What-If Simulator",
    "🗺️ Geospatial Hub Map"
])

# ------------------------------------------------------------------------------
# TAB 1: OPERATIONAL CONGESTION
# ------------------------------------------------------------------------------
with tab_congestion:
    st.subheader("Network Capacity & Corridor Transit Dynamics")
    st.markdown("Analyze top volume bottlenecks across terminal stations and corridor friction metrics.")

    col_chart1, col_chart2 = st.columns([1, 1], gap="medium")

    with col_chart1:
        st.markdown("##### 🏆 Top 10 Stations by Scheduled Transits")
        # Top 10 stations by total_trains_handled
        top10_stations = df_stations.nlargest(10, "total_trains_handled").copy()
        # Sort ascending for clean horizontal bar presentation
        top10_stations = top10_stations.sort_values(by="total_trains_handled", ascending=True)

        fig_bar = px.bar(
            top10_stations,
            x="total_trains_handled",
            y="station_name",
            orientation="h",
            color="total_trains_handled",
            color_continuous_scale="Blues",
            labels={
                "total_trains_handled": "Total Trains Handled",
                "station_name": "Station Name",
                "station_code": "Station Code",
                "avg_halt_min": "Avg Halt (min)",
                "total_anomalies": "Anomalies"
            },
            hover_data=["station_code", "avg_halt_min", "total_anomalies"],
            title="Scheduled Train Traffic Volume at Top 10 Junctions"
        )
        fig_bar.update_layout(
            height=480,
            margin=dict(l=20, r=20, t=40, b=20),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="#e2e8f0"),
            yaxis=dict(autorange=True)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        st.markdown("##### ⚠️ Corridor Distance vs. Halt Friction (Anomalies)")
        # Scatter plot of corridor total_distance_km vs. total_halt_duration_min, sized by anomaly_stops, red palette
        fig_scatter = px.scatter(
            df_routes,
            x="total_distance_km",
            y="total_halt_duration_min",
            size="anomaly_stops",
            color="anomaly_stops",
            color_continuous_scale="Reds",
            hover_name="train_name",
            hover_data={
                "train_no": True,
                "total_stops": True,
                "total_distance_km": ":.1f",
                "total_halt_duration_min": ":.1f",
                "anomaly_stops": True
            },
            labels={
                "total_distance_km": "Corridor Distance (km)",
                "total_halt_duration_min": "Total Scheduled Halt Duration (min)",
                "anomaly_stops": "Flagged Anomalies"
            },
            title="Corridor Distance vs. Total Halt Duration (Sized by Bottlenecks)"
        )
        fig_scatter.update_layout(
            height=480,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(gridcolor="#e2e8f0"),
            yaxis=dict(gridcolor="#e2e8f0")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Detailed Interactive Data Explorer Expander
    with st.expander("🔍 Explore Filterable Station & Route Performance Tables"):
        st_col, rt_col = st.columns(2)
        with st_col:
            st.markdown("**Top Station Junctions**")
            st.dataframe(
                df_stations[["station_code", "station_name", "total_trains_handled", "avg_halt_min", "total_anomalies"]].head(25),
                use_container_width=True
            )
        with rt_col:
            st.markdown("**Top Route Corridors**")
            st.dataframe(
                df_routes[["train_no", "train_name", "total_stops", "total_distance_km", "total_halt_duration_min", "anomaly_stops"]].head(25),
                use_container_width=True
            )


# ------------------------------------------------------------------------------
# TAB 2: INTERACTIVE WHAT-IF SIMULATOR
# ------------------------------------------------------------------------------
with tab_what_if:
    st.subheader("🎯 Smart-Signaling & Dwell Friction Reduction Simulator")
    st.markdown("""
    Evaluate systemic transit capacity gains through automated signaling, AI platform dispatching, 
    and optimized junction dwell times across the Indian Railways network.
    """)

    sim_col1, sim_col2 = st.columns([1, 2], gap="large")

    with sim_col1:
        st.markdown("#### Scenario Control")
        # Dynamic slider (0% to 30%, default 15%)
        dwell_reduction_pct = st.slider(
            "Select Dwell Friction Reduction (%):",
            min_value=0,
            max_value=30,
            value=15,
            step=1,
            help="Simulates percentage dwell reduction achieved via electronic interlocking and dynamic platform scheduling."
        )

        # Real-time KPI delta recalculation against baseline 6,897.60 daily hours
        baseline_hours = BASELINE_DAILY_HOURS
        hours_saved_daily = baseline_hours * (dwell_reduction_pct / 100.0)
        projected_hours_daily = baseline_hours - hours_saved_daily
        annual_hours_saved = hours_saved_daily * 365

        st.markdown("---")
        st.metric(
            label="Baseline Cumulative Daily Dwell",
            value=f"{baseline_hours:,.2f} hrs"
        )
        st.metric(
            label="Projected Network Daily Dwell",
            value=f"{projected_hours_daily:,.2f} hrs",
            delta=f"-{hours_saved_daily:,.2f} hrs/day ({dwell_reduction_pct}%)",
            delta_color="normal"
        )
        st.metric(
            label="Annual Operational Hours Saved",
            value=f"{annual_hours_saved:,.1f} hrs/year",
            delta=f"+{(annual_hours_saved/24):,.0f} Train-Days Recovered",
            delta_color="inverse"
        )

    with sim_col2:
        st.markdown("#### Real-Time Scenario Sensitivity Projection")
        
        # Build sensitivity curve for range 0% to 30%
        curve_pcts = list(range(0, 31, 2))
        curve_saved = [baseline_hours * (p / 100.0) for p in curve_pcts]
        curve_total = [baseline_hours - s for s in curve_saved]

        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(
            x=curve_pcts,
            y=curve_total,
            mode="lines+markers",
            name="Projected Dwell Hours",
            line=dict(color="#0d3b66", width=3)
        ))
        # Marker for current slider position
        fig_sim.add_trace(go.Scatter(
            x=[dwell_reduction_pct],
            y=[projected_hours_daily],
            mode="markers",
            name=f"Current Selection ({dwell_reduction_pct}%)",
            marker=dict(color="#e11d48", size=14, symbol="diamond")
        ))
        fig_sim.update_layout(
            title="Network Dwell Hours vs. Optimization Intensity",
            xaxis_title="Dwell Reduction (%)",
            yaxis_title="Total Daily Dwell (Hours)",
            height=340,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(gridcolor="#e2e8f0"),
            yaxis=dict(gridcolor="#e2e8f0")
        )
        st.plotly_chart(fig_sim, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📋 Pre-Configured Benchmark Scenarios (What_If_Model Table)")
    st.dataframe(df_what_if, use_container_width=True, hide_index=True)


# ------------------------------------------------------------------------------
# TAB 3: GEOSPATIAL HUB MAP
# ------------------------------------------------------------------------------
with tab_geo:
    st.subheader("🗺️ Strategic Railway Junction Geospatial Network")
    st.markdown("""
    Interactive geographic distribution of top critical hubs across Indian Railways.
    Nodes are dynamically sized by scheduled transit capacity and color-coded by anomaly concentration.
    """)

    if os.path.isfile(GEO_MAP_PATH):
        try:
            with open(GEO_MAP_PATH, "r", encoding="utf-8") as f:
                map_html = f.read()

            st.caption(f"📍 Displaying embedded Folium Leaflet interactive visualization (`{GEO_MAP_PATH}`)")
            components.html(map_html, height=620, scrolling=True)
            
            with open(GEO_MAP_PATH, "rb") as f_down:
                st.download_button(
                    label="⬇️ Download Standalone HTML Map",
                    data=f_down,
                    file_name="interactive_transit_map.html",
                    mime="text/html"
                )
        except Exception as e:
            st.error(f"Error loading map file: {str(e)}")
    else:
        st.warning(f"⚠️ Geospatial map file not detected at `{GEO_MAP_PATH}`.")
        st.markdown("""
        To generate the interactive Folium transit map, run:
        ```bash
        python src/04_geospatial_map.py
        ```
        or run the master orchestrator:
        ```bash
        python main.py
        ```
        """)


# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.85rem; padding: 10px;'>"
    "Indian Railways Transit Analytics Platform • B.Tech PBL (CSE0521) • Powered by Python, Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True
)
