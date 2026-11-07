#!/usr/bin/env python3
"""
Task 5: City of Sydney Property Valuation Estimation
Target: Predict sale price as at 31 August 2026 for 181,711 flats.
Output columns: gnaf_id, value (whole dollars, no $, no commas)
Judged on: % within 10% on 227 private sales under $1.2M, tie-break by median absolute dollar error.
"""

import sys
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score

DATA_DIR = os.path.abspath("task5-valuation")
OUTPUT_PATH = os.path.abspath("submission/valuation_oneshot.csv")
TARGET_DATE = pd.to_datetime("2026-08-31")
CBD_LAT, CBD_LON = -33.8688, 151.2093

def load_and_preprocess():
    print("Loading Task 5 datasets...")
    flats_path = os.path.join(DATA_DIR, "flats-city-of-sydney.csv")
    sales_path = os.path.join(DATA_DIR, "flat-sales-city-of-sydney.csv")
    repeat_path = os.path.join(DATA_DIR, "repeat-sales-city-of-sydney.csv")
    blocks_path = os.path.join(DATA_DIR, "blocks-homes-and-people-2021-2026.csv")

    df_flats = pd.read_csv(flats_path)
    df_sales = pd.read_csv(sales_path)
    df_repeat = pd.read_csv(repeat_path)
    df_blocks = pd.read_csv(blocks_path)

    # 1. Clean sales dates & filter <= 2026-08-31
    df_sales["sold_date"] = pd.to_datetime(df_sales["sold_date"], errors="coerce")
    df_sales = df_sales[df_sales["sold_date"] <= TARGET_DATE].copy()
    df_sales = df_sales[df_sales["price"].notna() & (df_sales["price"] >= 100000) & (df_sales["price"] <= 30000000)].copy()

    # 2. Compute suburb-level appreciation rates from repeat sales
    suburb_growth = df_repeat.groupby("suburb")["growth_pct_a_year"].median() / 100.0
    overall_median_growth = df_repeat["growth_pct_a_year"].median() / 100.0
    print(f"Overall median annual capital growth from repeat sales: {overall_median_growth*100:.2f}%/yr")

    # 3. Create mapping of each gnaf_id to its most recent sale
    latest_sales = df_sales.sort_values("sold_date").groupby("gnaf_id").last().reset_index()
    latest_sales_dict = latest_sales.set_index("gnaf_id")[["price", "sold_date"]].to_dict(orient="index")

    # 4. Flats attribute lookup
    flats_attr_dict = df_flats.set_index("gnaf_id")[["bedrooms", "bathrooms", "car_spaces", "flats_in_building", "latitude", "longitude", "suburb", "block_type"]].to_dict(orient="index")

    # Enrich sales dataset for Hedonic training
    def enrich_sales(sales_df):
        res = sales_df.copy()
        
        # Merge missing attributes from flats table
        res["flats_beds"] = res["gnaf_id"].map(lambda x: flats_attr_dict.get(x, {}).get("bedrooms", np.nan))
        res["flats_baths"] = res["gnaf_id"].map(lambda x: flats_attr_dict.get(x, {}).get("bathrooms", np.nan))
        res["flats_cars"] = res["gnaf_id"].map(lambda x: flats_attr_dict.get(x, {}).get("car_spaces", np.nan))
        res["flats_in_bldg"] = res["gnaf_id"].map(lambda x: flats_attr_dict.get(x, {}).get("flats_in_building", np.nan))
        res["flats_lat"] = res["gnaf_id"].map(lambda x: flats_attr_dict.get(x, {}).get("latitude", np.nan))
        res["flats_lon"] = res["gnaf_id"].map(lambda x: flats_attr_dict.get(x, {}).get("longitude", np.nan))
        res["flats_block_type"] = res["gnaf_id"].map(lambda x: flats_attr_dict.get(x, {}).get("block_type", "Residential"))

        res["bedrooms"] = pd.to_numeric(res["bedrooms"].fillna(res["flats_beds"]), errors="coerce").fillna(1.0)
        res["bathrooms"] = pd.to_numeric(res["bathrooms"].fillna(res["flats_baths"]), errors="coerce").fillna(1.0)
        res["car_spaces"] = pd.to_numeric(res["car_spaces"].fillna(res["flats_cars"]), errors="coerce").fillna(0.0)
        res["flats_in_building"] = pd.to_numeric(res["flats_in_bldg"], errors="coerce").fillna(20.0)

        lat = pd.to_numeric(res["flats_lat"], errors="coerce").fillna(CBD_LAT)
        lon = pd.to_numeric(res["flats_lon"], errors="coerce").fillna(CBD_LON)
        res["latitude"] = lat
        res["longitude"] = lon
        res["dist_to_cbd"] = np.sqrt((lat - CBD_LAT)**2 + (lon - CBD_LON)**2)

        res["suburb"] = res["suburb"].astype(str).fillna("Unknown")
        res["block_type"] = res["flats_block_type"].astype(str).fillna("Residential")

        # Time difference to target date
        res["years_to_target"] = (TARGET_DATE - res["sold_date"]).dt.total_seconds() / (365.25 * 86400)
        res["years_to_target"] = res["years_to_target"].clip(lower=0.0)

        return res

    df_sales_enriched = enrich_sales(df_sales)

    # Enrich test flats
    df_flats_enriched = df_flats.copy()
    df_flats_enriched["bedrooms"] = pd.to_numeric(df_flats_enriched["bedrooms"], errors="coerce").fillna(1.0)
    df_flats_enriched["bathrooms"] = pd.to_numeric(df_flats_enriched["bathrooms"], errors="coerce").fillna(1.0)
    df_flats_enriched["car_spaces"] = pd.to_numeric(df_flats_enriched["car_spaces"], errors="coerce").fillna(0.0)
    df_flats_enriched["flats_in_building"] = pd.to_numeric(df_flats_enriched["flats_in_building"], errors="coerce").fillna(20.0)

    lat = pd.to_numeric(df_flats_enriched["latitude"], errors="coerce").fillna(CBD_LAT)
    lon = pd.to_numeric(df_flats_enriched["longitude"], errors="coerce").fillna(CBD_LON)
    df_flats_enriched["latitude"] = lat
    df_flats_enriched["longitude"] = lon
    df_flats_enriched["dist_to_cbd"] = np.sqrt((lat - CBD_LAT)**2 + (lon - CBD_LON)**2)

    df_flats_enriched["suburb"] = df_flats_enriched["suburb"].astype(str).fillna("Unknown")
    df_flats_enriched["block_type"] = df_flats_enriched["block_type"].astype(str).fillna("Residential")
    df_flats_enriched["years_to_target"] = 0.0  # As-at target date

    return df_sales_enriched, df_flats_enriched, latest_sales_dict, suburb_growth, overall_median_growth

def train_and_predict(df_sales, df_flats, latest_sales_dict, suburb_growth, overall_growth):
    # Only train hedonic model on sales from 2017 onwards to keep relevant market pricing dynamics
    df_train = df_sales[df_sales["sold_date"] >= "2017-01-01"].copy()

    # Validation holdout: sales from 2026 under $1.2M
    val_mask = (df_train["sold_date"] >= "2026-01-01") & (df_train["price"] <= 1200000)
    train_split = df_train[~val_mask]
    val_split = df_train[val_mask]

    features = [
        "bedrooms", "bathrooms", "car_spaces", "flats_in_building",
        "latitude", "longitude", "dist_to_cbd", "years_to_target"
    ]
    
    all_suburbs = {s: i for i, s in enumerate(sorted(set(df_sales["suburb"]).union(set(df_flats["suburb"]))))}
    all_blocks = {b: i for i, b in enumerate(sorted(set(df_sales["block_type"]).union(set(df_flats["block_type"]))))}

    for df in [train_split, val_split, df_train, df_flats]:
        df["suburb_code"] = df["suburb"].map(all_suburbs).fillna(-1)
        df["block_type_code"] = df["block_type"].map(all_blocks).fillna(-1)

    model_features = features + ["suburb_code", "block_type_code"]
    cat_indices = [model_features.index("suburb_code"), model_features.index("block_type_code")]

    # Target: Log price to optimize relative percentage error
    y_train = np.log(train_split["price"])
    y_val = val_split["price"].values

    print(f"Training Hedonic Model on {len(train_split)} sales, validating on {len(val_split)} held-out 2026 sales < $1.2M...")

    hedonic_val = HistGradientBoostingRegressor(
        loss="absolute_error",
        max_iter=450,
        learning_rate=0.06,
        max_leaf_nodes=75,
        min_samples_leaf=20,
        categorical_features=cat_indices,
        random_state=42
    )
    hedonic_val.fit(train_split[model_features], y_train)

    val_log_preds = hedonic_val.predict(val_split[model_features])
    val_preds = np.exp(val_log_preds)

    # Evaluate validation accuracy: % within 10%
    pct_diff = np.abs(val_preds - y_val) / y_val
    within_10 = np.mean(pct_diff <= 0.10) * 100
    within_15 = np.mean(pct_diff <= 0.15) * 100
    median_abs_err = np.median(np.abs(val_preds - y_val))
    r2 = r2_score(y_val, val_preds)

    print("=== Held-Out 2026 Validation Results (< $1.2M) ===")
    print(f"Share within 10% (Main Metric): {within_10:.2f}%")
    print(f"Share within 15%:               {within_15:.2f}%")
    print(f"Median Absolute Dollar Error:   ${median_abs_err:,.2f}")
    print(f"R-squared:                      {r2:.4f}")

    # Production Hedonic Model on all training sales
    print("Fitting production Hedonic model on all sales from 2017 to 2026...")
    prod_hedonic = HistGradientBoostingRegressor(
        loss="absolute_error",
        max_iter=500,
        learning_rate=0.05,
        max_leaf_nodes=80,
        min_samples_leaf=15,
        categorical_features=cat_indices,
        random_state=42
    )
    prod_hedonic.fit(df_train[model_features], np.log(df_train["price"]))

    print(f"Predicting valuation for all {len(df_flats)} City of Sydney flats...")
    hedonic_flats_preds = np.exp(prod_hedonic.predict(df_flats[model_features]))

    # Repeat-Sales & Blend Engine
    final_values = []
    blend_counts = {"recent_sale": 0, "mid_sale": 0, "old_sale": 0, "hedonic_only": 0}

    for idx, row in df_flats.iterrows():
        gnaf = row["gnaf_id"]
        hedonic_val = hedonic_flats_preds[idx]
        suburb = row["suburb"]
        suburb_cagr = suburb_growth.get(suburb, overall_growth)
        # Cap CAGR between 1% and 7% for safety
        suburb_cagr = np.clip(suburb_cagr, 0.01, 0.07)

        if gnaf in latest_sales_dict:
            last_price = latest_sales_dict[gnaf]["price"]
            last_date = latest_sales_dict[gnaf]["sold_date"]
            years = (TARGET_DATE - last_date).total_seconds() / (365.25 * 86400)
            indexed_price = last_price * ((1.0 + suburb_cagr) ** years)

            if last_date >= pd.to_datetime("2023-01-01"):
                # Recent sale: 75% indexed repeat sale, 25% hedonic
                val = 0.75 * indexed_price + 0.25 * hedonic_val
                blend_counts["recent_sale"] += 1
            elif last_date >= pd.to_datetime("2018-01-01"):
                # Mid sale: 45% indexed, 55% hedonic
                val = 0.45 * indexed_price + 0.55 * hedonic_val
                blend_counts["mid_sale"] += 1
            else:
                # Older sale: 20% indexed, 80% hedonic
                val = 0.20 * indexed_price + 0.80 * hedonic_val
                blend_counts["old_sale"] += 1
        else:
            val = hedonic_val
            blend_counts["hedonic_only"] += 1

        # Clip reasonable Sydney flat prices
        val = np.clip(val, 250000.0, 25000000.0)
        final_values.append(int(round(val)))

    print("Valuation Blend Statistics:")
    print(blend_counts)

    assert len(final_values) == 181711, f"Expected 181711 rows, got {len(final_values)}"
    assert np.all(np.array(final_values) > 0), "Found non-positive values!"

    submission = pd.DataFrame({
        "gnaf_id": df_flats["gnaf_id"],
        "value": final_values
    })

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    submission.to_csv(OUTPUT_PATH, index=False)
    print(f"Successfully saved {len(submission)} rows to {OUTPUT_PATH}")

    # Summary
    print("=== Valuation Prediction Summary ===")
    print(f"Median Valuation: ${submission['value'].median():,.0f}")
    print(f"Mean Valuation:   ${submission['value'].mean():,.0f}")
    print(f"25th Percentile:  ${submission['value'].quantile(0.25):,.0f}")
    print(f"75th Percentile:  ${submission['value'].quantile(0.75):,.0f}")

    return {
        "within_10": within_10,
        "within_15": within_15,
        "median_dollar_error": median_abs_err,
        "r2": r2,
        "rows": len(submission)
    }

if __name__ == "__main__":
    df_sales, df_flats, latest_sales, suburb_growth, overall_growth = load_and_preprocess()
    train_and_predict(df_sales, df_flats, latest_sales, suburb_growth, overall_growth)
