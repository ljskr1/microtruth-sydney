#!/usr/bin/env python3
"""
Task 4: City of Sydney Flat Rental Estimation
Target: Predict weekly asking rent at 31 July 2026 for 65,777 flats.
Output columns: gnaf_id, rent_with_car_space, rent_without_car_space
Judged on: Median Absolute Dollar Error (MAE) and % within $100.
"""

import sys
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score

DATA_DIR = os.path.abspath("task4-rents")
OUTPUT_PATH = os.path.abspath("submission/rents_oneshot.csv")
TARGET_DATE = pd.to_datetime("2026-07-31")
CBD_LAT, CBD_LON = -33.8688, 151.2093

def load_and_preprocess_data():
    print("Loading Task 4 datasets...")
    past_leases_path = os.path.join(DATA_DIR, "rents-past-leases-city-of-sydney.csv")
    input_flats_path = os.path.join(DATA_DIR, "rents-input-flats-city-of-sydney.csv")
    blocks_path = os.path.join(DATA_DIR, "blocks-homes-and-people-2021-2026.csv")

    df_past = pd.read_csv(past_leases_path)
    df_input = pd.read_csv(input_flats_path)
    df_blocks = pd.read_csv(blocks_path)

    # Clean dates and filter <= 2026-07-31
    df_past["listing_date"] = pd.to_datetime(df_past["listing_date"], errors="coerce")
    df_past = df_past[df_past["listing_date"] <= TARGET_DATE].copy()
    df_past = df_past[df_past["weekly_rent"].notna() & (df_past["weekly_rent"] > 100) & (df_past["weekly_rent"] < 10000)].copy()

    # Merge block demographics if mb present
    blocks_lookup = df_blocks.drop_duplicates(subset=["mb"]).set_index("mb")[["homes_2026", "people_2026", "new_homes"]].to_dict(orient="index")

    def enrich(df, is_train=True):
        res = df.copy()
        # Impute bedrooms / bathrooms
        res["bedrooms"] = pd.to_numeric(res["bedrooms"], errors="coerce")
        res["bathrooms"] = pd.to_numeric(res["bathrooms"], errors="coerce")
        
        # Bed imputation
        res["bedrooms"] = res["bedrooms"].fillna(1.0)
        res["bathrooms"] = res["bathrooms"].fillna(1.0)

        # Parking
        if "car_space" in res.columns:
            res["car_space_val"] = pd.to_numeric(res["car_space"], errors="coerce").fillna(0.0)
        elif "car_spaces" in res.columns:
            res["car_space_val"] = pd.to_numeric(res["car_spaces"], errors="coerce").fillna(0.0)
        else:
            res["car_space_val"] = 0.0

        # Geo distances
        lat = pd.to_numeric(res["latitude"], errors="coerce").fillna(CBD_LAT)
        lon = pd.to_numeric(res["longitude"], errors="coerce").fillna(CBD_LON)
        res["dist_to_cbd"] = np.sqrt((lat - CBD_LAT)**2 + (lon - CBD_LON)**2)
        res["latitude"] = lat
        res["longitude"] = lon

        # Block features
        res["homes_2026"] = res["mb"].map(lambda x: blocks_lookup.get(x, {}).get("homes_2026", np.nan))
        res["new_homes"] = res["mb"].map(lambda x: blocks_lookup.get(x, {}).get("new_homes", np.nan))

        # Time difference to target date in years
        if is_train:
            res["years_to_target"] = (TARGET_DATE - res["listing_date"]).dt.total_seconds() / (365.25 * 86400)
            res["years_to_target"] = res["years_to_target"].clip(lower=0.0)
        else:
            res["years_to_target"] = 0.0  # As-at target date

        # Categoricals
        res["suburb"] = res["suburb"].astype(str).fillna("Unknown")
        res["property_type"] = res["property_type"].astype(str).fillna("unit")

        return res

    df_train = enrich(df_past, is_train=True)
    df_test = enrich(df_input, is_train=False)

    return df_train, df_test

def train_and_predict(df_train, df_test):
    # Holdout validation split: leases in 2026 (Jan to July 2026) as validation set
    val_mask = df_train["listing_date"] >= "2026-01-01"
    train_split = df_train[~val_mask]
    val_split = df_train[val_mask]

    features = [
        "bedrooms", "bathrooms", "car_space_val",
        "latitude", "longitude", "dist_to_cbd",
        "homes_2026", "new_homes", "years_to_target"
    ]
    categorical_features = ["suburb", "property_type"]

    # String indexing for categoricals
    all_suburbs = {s: i for i, s in enumerate(sorted(set(df_train["suburb"]).union(set(df_test["suburb"]))))}
    all_types = {t: i for i, t in enumerate(sorted(set(df_train["property_type"]).union(set(df_test["property_type"]))))}

    for df in [train_split, val_split, df_train, df_test]:
        df["suburb_code"] = df["suburb"].map(all_suburbs).fillna(-1)
        df["type_code"] = df["property_type"].map(all_types).fillna(-1)

    model_features = features + ["suburb_code", "type_code"]
    cat_indices = [model_features.index("suburb_code"), model_features.index("type_code")]

    print(f"Training on {len(train_split)} rows, validating on {len(val_split)} held-out 2026 leases...")
    
    # Model using absolute error (MAE) to directly optimize median absolute error
    model_val = HistGradientBoostingRegressor(
        loss="absolute_error",
        max_iter=350,
        learning_rate=0.08,
        max_leaf_nodes=63,
        min_samples_leaf=20,
        categorical_features=cat_indices,
        random_state=42
    )
    
    model_val.fit(train_split[model_features], train_split["weekly_rent"])
    val_preds = model_val.predict(val_split[model_features])

    mae = mean_absolute_error(val_split["weekly_rent"], val_preds)
    median_err = np.median(np.abs(val_split["weekly_rent"] - val_preds))
    r2 = r2_score(val_split["weekly_rent"], val_preds)
    pct_within_100 = np.mean(np.abs(val_split["weekly_rent"] - val_preds) <= 100) * 100

    print("=== Held-Out 2026 Validation Results ===")
    print(f"Mean Absolute Error: ${mae:.2f}")
    print(f"Median Absolute Dollar Error: ${median_err:.2f}")
    print(f"R-squared: {r2:.4f}")
    print(f"Share within $100/wk: {pct_within_100:.2f}%")

    # Fit final model on all data <= 2026-07-31
    print("Fitting production model on full historical dataset (112k+ leases)...")
    prod_model = HistGradientBoostingRegressor(
        loss="absolute_error",
        max_iter=400,
        learning_rate=0.07,
        max_leaf_nodes=75,
        min_samples_leaf=15,
        categorical_features=cat_indices,
        random_state=42
    )
    prod_model.fit(df_train[model_features], df_train["weekly_rent"])

    # Predict test set with and without car space
    print(f"Generating predictions for {len(df_test)} flats...")
    
    # Copy with car space forced to 1
    df_test_with_car = df_test[model_features].copy()
    df_test_with_car["car_space_val"] = 1.0
    preds_with_car = prod_model.predict(df_test_with_car)

    # Copy with car space forced to 0
    df_test_no_car = df_test[model_features].copy()
    df_test_no_car["car_space_val"] = 0.0
    preds_no_car = prod_model.predict(df_test_no_car)

    # Post-process: parking premium must be >= 0
    # Sydney market baseline parking premium is typically $50-$120/wk
    parking_diff = np.maximum(preds_with_car - preds_no_car, 35.0)  # Minimum parking premium $35/wk
    final_with_car = preds_no_car + parking_diff

    # Round to whole numbers or 50 cents as allowed
    final_with_car = np.round(final_with_car * 2) / 2
    final_no_car = np.round(preds_no_car * 2) / 2

    # Verify no NaN or non-positive
    assert np.all(final_with_car > 0), "Found non-positive rent with car space!"
    assert np.all(final_no_car > 0), "Found non-positive rent without car space!"
    assert len(final_with_car) == 65777, f"Expected 65777 rows, got {len(final_with_car)}"

    submission = pd.DataFrame({
        "gnaf_id": df_test["gnaf_id"],
        "rent_with_car_space": final_with_car,
        "rent_without_car_space": final_no_car
    })

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    submission.to_csv(OUTPUT_PATH, index=False)
    print(f"Successfully saved {len(submission)} rows to {OUTPUT_PATH}")

    # Output stats
    print("=== Prediction Summary ===")
    print(f"Median Rent (with car): ${submission['rent_with_car_space'].median():.2f}")
    print(f"Median Rent (no car):   ${submission['rent_without_car_space'].median():.2f}")
    print(f"Median Parking Premium: ${(submission['rent_with_car_space'] - submission['rent_without_car_space']).median():.2f}")

    return {
        "mae": mae,
        "median_dollar_error": median_err,
        "r2": r2,
        "pct_within_100": pct_within_100,
        "rows": len(submission)
    }

if __name__ == "__main__":
    df_train, df_test = load_and_preprocess_data()
    train_and_predict(df_train, df_test)
