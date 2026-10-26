#!/usr/bin/env python3
"""
Railway Transit Analytics - Master Pipeline Orchestrator (main.py)
B.Tech Project-Based Learning (CSE0521) - Data Science & Analytics

Sequentially executes the end-to-end data lifecycle:
1. Unit 2: Automated Data Profiling (Sweetviz)
2. Unit 3: Data Wrangling & ML Anomaly Detection (Isolation Forest)
3. Unit 3: Statistical EDA & Hypothesis Testing (Mann-Whitney U)
4. Unit 4: Geospatial Transit Network Mapping (Folium)
5. Unit 5: Business Intelligence Data Pack Generation (Excel & CSV)
"""

import logging
import os
import subprocess
import sys
import time

# Configure logging with timestamps and professional formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("PipelineOrchestrator")

# Pipeline lifecycle sequence
PIPELINE_STAGES = [
    {
        "unit": "Unit 2",
        "name": "Automated Profiling & EDA",
        "script": os.path.join("src", "01_profile_data.py"),
        "description": "Generate Sweetviz baseline exploratory profiling report"
    },
    {
        "unit": "Unit 3",
        "name": "Wrangling & Isolation Forest Anomaly Detection",
        "script": os.path.join("src", "02_clean_and_engineer.py"),
        "description": "Clean raw records, engineer transit metrics, detect bottlenecks"
    },
    {
        "unit": "Unit 3",
        "name": "Statistical Hypothesis Testing & Visuals",
        "script": os.path.join("src", "03_statistical_eda.py"),
        "description": "Execute Mann-Whitney U test and render statistical distributions"
    },
    {
        "unit": "Unit 4",
        "name": "Geospatial Transit Network Mapping",
        "script": os.path.join("src", "04_geospatial_map.py"),
        "description": "Generate interactive Leaflet/Folium geospatial transit hub map"
    },
    {
        "unit": "Unit 5",
        "name": "BI Dashboard Data Pack Generation",
        "script": os.path.join("src", "05_export_dashboard_data.py"),
        "description": "Export structured Excel BI pack and scenario model tables"
    }
]


def run_stage(stage_info: dict) -> None:
    """Execute a single pipeline stage using subprocess with real-time output and error checking."""
    script_path = stage_info["script"]
    stage_name = stage_info["name"]
    unit = stage_info["unit"]

    logger.info("=" * 70)
    logger.info(f"STARTING [{unit}]: {stage_name}")
    logger.info(f"Target script: {script_path}")
    logger.info(f"Objective: {stage_info['description']}")
    logger.info("=" * 70)

    if not os.path.isfile(script_path):
        logger.error(f"Missing required script: {script_path}")
        sys.exit(1)

    start_time = time.time()

    # Execute script using current Python interpreter environment
    process = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    # Stream output in real time
    if process.stdout:
        for line in iter(process.stdout.readline, ""):
            print(line, end="")
        process.stdout.close()

    exit_code = process.wait()
    elapsed = time.time() - start_time

    if exit_code != 0:
        logger.error(f"STAGE FAILED: [{unit}] {stage_name} exited with non-zero code {exit_code}")
        logger.error(f"Execution halted immediately to prevent data corruption downstream.")
        sys.exit(exit_code)

    logger.info(f"COMPLETED [{unit}]: {stage_name} in {elapsed:.2f} seconds\n")


def main() -> None:
    """Execute the full data lifecycle orchestrator."""
    logger.info("======================================================================")
    logger.info("RAILWAY TRANSIT ANALYTICS: PIPELINE MASTER ORCHESTRATOR")
    logger.info("B.Tech Project-Based Learning (CSE0521) - Data Science & Analytics")
    logger.info("======================================================================")
    
    total_start_time = time.time()

    for idx, stage in enumerate(PIPELINE_STAGES, 1):
        logger.info(f"Executing Lifecycle Step {idx}/{len(PIPELINE_STAGES)}")
        run_stage(stage)

    total_elapsed = time.time() - total_start_time
    logger.info("======================================================================")
    logger.info(f"PIPELINE ORCHESTRATION COMPLETED SUCCESSFULLY in {total_elapsed:.2f} seconds!")
    logger.info("All artifacts, models, maps, and BI packages are ready for deployment.")
    logger.info("To launch the interactive dashboard, run: streamlit run src/app.py")
    logger.info("======================================================================")


if __name__ == "__main__":
    main()
