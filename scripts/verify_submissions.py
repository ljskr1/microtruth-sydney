#!/usr/bin/env python3
"""
Verification Script for Hackathon Official Submissions
Assures 100% adherence to Luke Metcalfe's scoring specification for Tasks 4 and 5.
"""

import sys
import os
import pandas as pd
import numpy as np

def verify_task4():
    print("--> Verifying Task 4: rents_oneshot.csv")
    path = "submission/rents_oneshot.csv"
    input_path = "task4-rents/rents-input-flats-city-of-sydney.csv"
    
    assert os.path.exists(path), f"File {path} does not exist!"
    assert os.path.exists(input_path), f"File {input_path} does not exist!"

    df_sub = pd.read_csv(path)
    df_inp = pd.read_csv(input_path)

    # 1. Row count
    assert len(df_sub) == 65777, f"Expected 65,777 rows, got {len(df_sub)}"
    assert len(df_sub) == len(df_inp), "Row count does not match input file!"

    # 2. Columns
    expected_cols = ["gnaf_id", "rent_with_car_space", "rent_without_car_space"]
    assert list(df_sub.columns) == expected_cols, f"Columns mismatch! Got {list(df_sub.columns)}"

    # 3. GNAF ID match
    assert (df_sub["gnaf_id"] == df_inp["gnaf_id"]).all(), "gnaf_id values do not match input in order!"

    # 4. Zero nulls / NaNs
    assert df_sub["rent_with_car_space"].notna().all(), "Found nulls in rent_with_car_space!"
    assert df_sub["rent_without_car_space"].notna().all(), "Found nulls in rent_without_car_space!"

    # 5. Positive numbers
    assert (df_sub["rent_with_car_space"] > 0).all(), "Found non-positive rent_with_car_space!"
    assert (df_sub["rent_without_car_space"] > 0).all(), "Found non-positive rent_without_car_space!"

    # 6. Parking premium is non-negative
    diff = df_sub["rent_with_car_space"] - df_sub["rent_without_car_space"]
    assert (diff >= 0).all(), "Found rent_with_car_space < rent_without_car_space!"

    print("    [PASS] Task 4 rents_oneshot.csv is 100% compliant!")
    print(f"    Total rows: {len(df_sub):,}")
    print(f"    Median Rent (with car):    ${df_sub['rent_with_car_space'].median():.2f}")
    print(f"    Median Rent (without car): ${df_sub['rent_without_car_space'].median():.2f}")
    print(f"    Median Parking Premium:    ${diff.median():.2f}")
    return True

def verify_task5():
    print("--> Verifying Task 5: valuation_oneshot.csv")
    path = "submission/valuation_oneshot.csv"
    input_path = "task5-valuation/flats-city-of-sydney.csv"

    assert os.path.exists(path), f"File {path} does not exist!"
    assert os.path.exists(input_path), f"File {input_path} does not exist!"

    df_sub = pd.read_csv(path)
    df_inp = pd.read_csv(input_path)

    # 1. Row count
    assert len(df_sub) == 181711, f"Expected 181,711 rows, got {len(df_sub)}"
    assert len(df_sub) == len(df_inp), "Row count does not match input file!"

    # 2. Columns
    expected_cols = ["gnaf_id", "value"]
    assert list(df_sub.columns) == expected_cols, f"Columns mismatch! Got {list(df_sub.columns)}"

    # 3. GNAF ID match
    assert (df_sub["gnaf_id"] == df_inp["gnaf_id"]).all(), "gnaf_id values do not match input in order!"

    # 4. Zero nulls / NaNs
    assert df_sub["value"].notna().all(), "Found nulls in value!"

    # 5. Positive integer dollars
    assert (df_sub["value"] > 0).all(), "Found non-positive value!"
    assert np.issubdtype(df_sub["value"].dtype, np.integer), "value column must be integer whole dollars!"

    print("    [PASS] Task 5 valuation_oneshot.csv is 100% compliant!")
    print(f"    Total rows: {len(df_sub):,}")
    print(f"    Median Valuation: ${df_sub['value'].median():,.0f}")
    print(f"    Min Valuation:    ${df_sub['value'].min():,.0f}")
    print(f"    Max Valuation:    ${df_sub['value'].max():,.0f}")
    return True

if __name__ == "__main__":
    t4 = verify_task4()
    t5 = verify_task5()
    if t4 and t5:
        print("\nALL SUBMISSIONS VERIFIED AND 100% READY FOR SUBMISSION!")
