import numpy as np
import pandas as pd
import pytest


def parse_time_to_minutes(time_series: pd.Series) -> pd.Series:
    """Convert timestamp strings (HH:MM:SS) to minutes elapsed from midnight."""
    parts = time_series.astype(str).str.split(":", expand=True)
    hours = pd.to_numeric(parts[0], errors="coerce").fillna(0)
    minutes = pd.to_numeric(parts[1], errors="coerce").fillna(0)
    return hours * 60 + minutes


def compute_dwell_time(df: pd.DataFrame) -> pd.Series:
    """
    Computes dwell/halt duration in minutes adhering to Indian Railways transit rules:
    - Origin station (arrival '0:00:00' or '00:00:00') -> 0.0 min halt
    - Terminus station (departure '0:00:00' or '00:00:00') -> 0.0 min halt
    - Midnight rollover transition handled via modulo 1440
    """
    arr_min = parse_time_to_minutes(df["arrival_time"])
    dep_min = parse_time_to_minutes(df["departure_time"])

    # Modulo-1440 midnight transition handling:
    # (dep_min - arr_min) % 1440 converts negative differences (e.g. 15 - 1430 = -1415 -> 25)
    halt = (dep_min - arr_min) % 1440

    # Boundary conditions for origin and terminus stops
    is_origin = df["arrival_time"].isin(["0:00:00", "00:00:00"])
    is_terminus = df["departure_time"].isin(["0:00:00", "00:00:00"])
    is_origin_or_terminus = is_origin | is_terminus

    return pd.Series(np.where(is_origin_or_terminus, 0.0, halt), index=df.index, dtype=float)


def compute_segment_distance(df: pd.DataFrame) -> pd.Series:
    """Computes non-negative inter-station segment distances along corridors."""
    prev_distance = df.groupby("train_no")["distance"].shift(1).fillna(0)
    segment_dist = df["distance"] - prev_distance
    return segment_dist.clip(lower=0.0)


# ==============================================================================
# TEST SUITE
# ==============================================================================

def test_standard_dwell_calculation():
    """
    Test 1: Standard dwell calculation
    Example: arrival '10:00:00' and departure '10:10:00' -> exactly 10.0 min.
    """
    sample_df = pd.DataFrame({
        "train_no": ["12001"],
        "arrival_time": ["10:00:00"],
        "departure_time": ["10:10:00"]
    })
    dwell = compute_dwell_time(sample_df)
    assert dwell.iloc[0] == pytest.approx(10.0), f"Expected 10.0 min dwell, got {dwell.iloc[0]}"


def test_midnight_rollover_modulo_1440():
    """
    Test 2: Midnight rollover modulo-1440 transition
    Example: arrival '23:50:00' and departure '00:15:00' -> exactly 25.0 min.
    """
    sample_df = pd.DataFrame({
        "train_no": ["12951", "12952"],
        "arrival_time": ["23:50:00", "23:45:00"],
        "departure_time": ["00:15:00", "00:05:00"]
    })
    dwell = compute_dwell_time(sample_df)
    assert dwell.iloc[0] == pytest.approx(25.0), f"Expected 25.0 min dwell for 23:50 -> 00:15, got {dwell.iloc[0]}"
    assert dwell.iloc[1] == pytest.approx(20.0), f"Expected 20.0 min dwell for 23:45 -> 00:05, got {dwell.iloc[1]}"


def test_origin_and_terminus_boundary_conditions():
    """
    Test 3: Origin and Terminus boundary conditions
    Example: arrival '00:00:00' or departure '00:00:00' (or '0:00:00') -> exactly 0.0 min.
    """
    sample_df = pd.DataFrame({
        "train_no": ["12002", "12002", "12003", "12003"],
        "arrival_time": ["00:00:00", "14:30:00", "0:00:00", "18:00:00"],
        "departure_time": ["06:00:00", "00:00:00", "07:15:00", "0:00:00"]
    })
    dwell = compute_dwell_time(sample_df)
    
    # Origin station 1 (arrival 00:00:00)
    assert dwell.iloc[0] == pytest.approx(0.0), f"Origin station dwell must be 0.0, got {dwell.iloc[0]}"
    # Terminus station 1 (departure 00:00:00)
    assert dwell.iloc[1] == pytest.approx(0.0), f"Terminus station dwell must be 0.0, got {dwell.iloc[1]}"
    # Origin station 2 (arrival 0:00:00)
    assert dwell.iloc[2] == pytest.approx(0.0), f"Origin station dwell with 0:00:00 must be 0.0, got {dwell.iloc[2]}"
    # Terminus station 2 (departure 0:00:00)
    assert dwell.iloc[3] == pytest.approx(0.0), f"Terminus station dwell with 0:00:00 must be 0.0, got {dwell.iloc[3]}"


def test_positive_segment_distance_calculation():
    """
    Test 4: Positive segment distance calculation test.
    Verifies that segment distances are strictly non-negative and properly computed
    from cumulative route distances.
    """
    sample_df = pd.DataFrame({
        "train_no": ["12001", "12001", "12001", "12002", "12002"],
        "seq": [1, 2, 3, 1, 2],
        "distance": [0, 50, 185, 0, 42]
    })
    segment_distances = compute_segment_distance(sample_df)
    
    # Assert all values are non-negative
    assert (segment_distances >= 0.0).all(), "Segment distances cannot be negative."
    
    # Check specific segment values
    assert segment_distances.iloc[0] == pytest.approx(0.0)    # Origin stop
    assert segment_distances.iloc[1] == pytest.approx(50.0)   # 50 - 0 = 50
    assert segment_distances.iloc[2] == pytest.approx(135.0)  # 185 - 50 = 135
    assert segment_distances.iloc[3] == pytest.approx(0.0)    # Origin of train 12002
    assert segment_distances.iloc[4] == pytest.approx(42.0)   # 42 - 0 = 42
