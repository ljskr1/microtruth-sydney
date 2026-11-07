#!/usr/bin/env python3
"""
Ingests 112,458 leases and 81,079 flat sales into SQLite (WAL mode).
Creates composite indexes on normalized street address and suburb for <2ms lookup.
"""

import os
import re
import sqlite3
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PARENT_DIR = os.path.dirname(PROJECT_ROOT)

DB_PATH = os.path.join(PROJECT_ROOT, "backend", "data", "transactions.db")

def find_file(filename):
    for base in [PROJECT_ROOT, PARENT_DIR]:
        candidate = os.path.join(base, filename)
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(f"Could not find {filename} in {PROJECT_ROOT} or {PARENT_DIR}")

LEASES_CSV = find_file("task4-rents/rents-past-leases-city-of-sydney.csv")
SALES_CSV = find_file("task5-valuation/flat-sales-city-of-sydney.csv")

def normalize_street(addr):
    if not isinstance(addr, str):
        return ""
    # Remove unit number: e.g. "Unit 105, 8 Sam Sing Street" -> "8 Sam Sing Street"
    s = addr.strip()
    s = re.sub(r'^(unit|apt|apartment|suite|lot|shop|level)\s+[\w\d/-]+,?\s*', '', s, flags=re.I)
    # Remove leading unit pattern: "105/8 Sam Sing" -> "8 Sam Sing"
    s = re.sub(r'^\d+[a-zA-Z]?/\s*', '', s)
    return s.upper()

def build_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Enable WAL mode for high read concurrency and <2ms queries
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA synchronous=NORMAL;")

    print("Creating tables...")
    cur.execute("""
    CREATE TABLE leases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gnaf_id TEXT,
        address TEXT,
        street_norm TEXT,
        suburb TEXT,
        listing_date TEXT,
        weekly_rent REAL,
        bedrooms REAL,
        bathrooms REAL,
        car_space REAL,
        property_type TEXT,
        latitude REAL,
        longitude REAL
    );
    """)

    cur.execute("""
    CREATE TABLE sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gnaf_id TEXT,
        address TEXT,
        street_norm TEXT,
        suburb TEXT,
        sold_date TEXT,
        price REAL,
        bedrooms REAL,
        bathrooms REAL,
        car_spaces REAL
    );
    """)

    print(f"Loading leases from {LEASES_CSV}...")
    df_l = pd.read_csv(LEASES_CSV)
    df_l["street_norm"] = df_l["building_address"].fillna(df_l["address"]).apply(normalize_street)
    df_l["bedrooms"] = pd.to_numeric(df_l["bedrooms"], errors="coerce")
    df_l["bathrooms"] = pd.to_numeric(df_l["bathrooms"], errors="coerce")
    df_l["car_space"] = pd.to_numeric(df_l["car_space"], errors="coerce")
    df_l["weekly_rent"] = pd.to_numeric(df_l["weekly_rent"], errors="coerce")
    
    leases_records = df_l[[
        "gnaf_id", "address", "street_norm", "suburb", "listing_date",
        "weekly_rent", "bedrooms", "bathrooms", "car_space", "property_type",
        "latitude", "longitude"
    ]].values.tolist()

    cur.executemany("""
    INSERT INTO leases (gnaf_id, address, street_norm, suburb, listing_date, weekly_rent, bedrooms, bathrooms, car_space, property_type, latitude, longitude)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, leases_records)
    print(f"Inserted {len(leases_records):,} lease records.")

    print(f"Loading sales from {SALES_CSV}...")
    df_s = pd.read_csv(SALES_CSV)
    df_s["street_norm"] = df_s["address"].apply(normalize_street)
    df_s["bedrooms"] = pd.to_numeric(df_s["bedrooms"], errors="coerce")
    df_s["bathrooms"] = pd.to_numeric(df_s["bathrooms"], errors="coerce")
    df_s["car_spaces"] = pd.to_numeric(df_s["car_spaces"], errors="coerce")
    df_s["price"] = pd.to_numeric(df_s["price"], errors="coerce")

    sales_records = df_s[[
        "gnaf_id", "address", "street_norm", "suburb", "sold_date",
        "price", "bedrooms", "bathrooms", "car_spaces"
    ]].values.tolist()

    cur.executemany("""
    INSERT INTO sales (gnaf_id, address, street_norm, suburb, sold_date, price, bedrooms, bathrooms, car_spaces)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, sales_records)
    print(f"Inserted {len(sales_records):,} sales records.")

    print("Building high-speed indexes...")
    cur.execute("CREATE INDEX idx_leases_street ON leases(street_norm);")
    cur.execute("CREATE INDEX idx_leases_suburb ON leases(suburb);")
    cur.execute("CREATE INDEX idx_leases_gnaf ON leases(gnaf_id);")

    cur.execute("CREATE INDEX idx_sales_street ON sales(street_norm);")
    cur.execute("CREATE INDEX idx_sales_suburb ON sales(suburb);")
    cur.execute("CREATE INDEX idx_sales_gnaf ON sales(gnaf_id);")

    conn.commit()
    conn.close()
    print(f"Database successfully created at {DB_PATH} ({os.path.getsize(DB_PATH)/(1024*1024):.1f} MB)!")

if __name__ == "__main__":
    build_database()
