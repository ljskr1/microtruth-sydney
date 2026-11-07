#!/usr/bin/env python3
"""
Ingest Task 2 & 3 Datasets:
1. addresses-city-of-sydney.csv (213k official G-NAF addresses in City of Sydney)
2. public-housing-homes-city-of-sydney.csv (6.5k estimated public housing homes)
Adds tables 'public_housing' and 'city_addresses' to backend/data/transactions.db.
"""

import os
import re
import sqlite3
import pandas as pd

DB_PATH = "backend/data/transactions.db"
HOUSING_CSV = "task2-3-ar-chrome/public-housing-homes-city-of-sydney.csv"
ADDRESSES_CSV = "task2-3-ar-chrome/addresses-city-of-sydney.csv"

def normalize_street(addr):
    if not isinstance(addr, str):
        return ""
    s = addr.strip()
    s = re.sub(r'^(unit|apt|apartment|suite|lot|shop|level)\s+[\w\d/-]+,?\s*', '', s, flags=re.I)
    s = re.sub(r'^\d+[a-zA-Z]?/\s*', '', s)
    s = re.split(r',', s)[0]
    return s.strip().upper()

def find_file(filename):
    for base in [".", "..", "task2-3-ar-chrome", "../task2-3-ar-chrome", "/Users/lijah/Desktop/task2-3-ar-chrome"]:
        candidate = os.path.join(base, os.path.basename(filename))
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(f"Could not find {filename}")

def ingest():
    db_file = DB_PATH
    if not os.path.exists(db_file) and os.path.exists(os.path.join("..", db_file)):
        db_file = os.path.join("..", db_file)

    housing_file = find_file(HOUSING_CSV)
    addresses_file = find_file(ADDRESSES_CSV)

    print(f"Connecting to database {db_file}...")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA synchronous=NORMAL;")

    print("Creating table public_housing...")
    cur.execute("DROP TABLE IF EXISTS public_housing;")
    cur.execute("""
    CREATE TABLE public_housing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gnaf_pid TEXT,
        address TEXT,
        street_norm TEXT,
        suburb TEXT,
        mb TEXT,
        lat REAL,
        lon REAL,
        confidence_score INTEGER
    );
    """)

    print(f"Loading {housing_file}...")
    df_h = pd.read_csv(housing_file)
    df_h["street_norm"] = df_h["address"].apply(normalize_street)
    df_h["lat"] = pd.to_numeric(df_h["lat"], errors="coerce")
    df_h["lon"] = pd.to_numeric(df_h["lon"], errors="coerce")
    df_h["confidence_score"] = pd.to_numeric(df_h["confidence_score"], errors="coerce").fillna(1)
    df_h["mb"] = df_h["mb"].astype(str)

    records_h = df_h[[
        "gnaf_pid", "address", "street_norm", "suburb", "mb", "lat", "lon", "confidence_score"
    ]].values.tolist()

    cur.executemany("""
    INSERT INTO public_housing (gnaf_pid, address, street_norm, suburb, mb, lat, lon, confidence_score)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, records_h)
    print(f"Inserted {len(records_h):,} public housing records.")

    print("Creating indexes on public_housing...")
    cur.execute("CREATE INDEX idx_housing_gnaf ON public_housing(gnaf_pid);")
    cur.execute("CREATE INDEX idx_housing_street ON public_housing(street_norm);")
    cur.execute("CREATE INDEX idx_housing_mb ON public_housing(mb);")
    cur.execute("CREATE INDEX idx_housing_suburb ON public_housing(suburb);")

    print("Creating table city_addresses...")
    cur.execute("DROP TABLE IF EXISTS city_addresses;")
    cur.execute("""
    CREATE TABLE city_addresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gnaf_id TEXT,
        address TEXT,
        street_norm TEXT,
        suburb TEXT,
        postcode TEXT,
        mb TEXT,
        latitude REAL,
        longitude REAL,
        register_type TEXT
    );
    """)

    print(f"Loading {addresses_file}...")
    df_a = pd.read_csv(addresses_file)
    df_a["street_norm"] = df_a["address"].apply(normalize_street)
    df_a["latitude"] = pd.to_numeric(df_a["latitude"], errors="coerce")
    df_a["longitude"] = pd.to_numeric(df_a["longitude"], errors="coerce")
    df_a["mb"] = df_a["mb"].astype(str)
    df_a["postcode"] = df_a["postcode"].astype(str)

    records_a = df_a[[
        "gnaf_id", "address", "street_norm", "suburb", "postcode", "mb", "latitude", "longitude", "register_type"
    ]].values.tolist()

    cur.executemany("""
    INSERT INTO city_addresses (gnaf_id, address, street_norm, suburb, postcode, mb, latitude, longitude, register_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, records_a)
    print(f"Inserted {len(records_a):,} city address records.")

    print("Creating indexes on city_addresses...")
    cur.execute("CREATE INDEX idx_addr_gnaf ON city_addresses(gnaf_id);")
    cur.execute("CREATE INDEX idx_addr_street ON city_addresses(street_norm);")
    cur.execute("CREATE INDEX idx_addr_suburb ON city_addresses(suburb);")

    conn.commit()
    conn.close()
    print("Task 2 & 3 ingestion complete!")

if __name__ == "__main__":
    ingest()
