import os
import re
import sqlite3
import time
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "transactions.db")

def normalize_street(addr: str) -> str:
    if not addr:
        return ""
    s = addr.strip()
    s = re.sub(r'^(unit|apt|apartment|suite|lot|shop|level)\s+[\w\d/-]+,?\s*', '', s, flags=re.I)
    s = re.sub(r'^\d+[a-zA-Z]?/\s*', '', s)
    # Strip suburb if separated by comma or postcode
    s = re.split(r',', s)[0]
    return s.strip().upper()

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Transactions database not found at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_building_comps(address: str, limit: int = 5) -> Dict[str, Any]:
    t0 = time.perf_counter()
    street_norm = normalize_street(address)
    if not street_norm:
        return {"error": "Invalid address", "sales": [], "leases": []}

    conn = get_db_connection()
    cur = conn.cursor()

    # Query matching sales
    cur.execute("""
        SELECT address, sold_date, price, bedrooms, bathrooms, car_spaces
        FROM sales
        WHERE street_norm = ? OR street_norm LIKE ?
        ORDER BY sold_date DESC
        LIMIT ?
    """, (street_norm, f"{street_norm}%", limit))
    sales = [dict(row) for row in cur.fetchall()]

    # Query matching leases
    cur.execute("""
        SELECT address, listing_date, weekly_rent, bedrooms, bathrooms, car_space
        FROM leases
        WHERE street_norm = ? OR street_norm LIKE ?
        ORDER BY listing_date DESC
        LIMIT ?
    """, (street_norm, f"{street_norm}%", limit))
    leases = [dict(row) for row in cur.fetchall()]

    conn.close()
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # Calculate building statistics
    sale_prices = [s["price"] for s in sales if s.get("price")]
    lease_rents = [l["weekly_rent"] for l in leases if l.get("weekly_rent")]

    return {
        "searched_address": address,
        "normalized_building_street": street_norm,
        "query_time_ms": round(elapsed_ms, 2),
        "recent_sales": sales,
        "recent_leases": leases,
        "building_stats": {
            "sales_count": len(sales),
            "leases_count": len(leases),
            "building_median_sale": int(sum(sale_prices) / len(sale_prices)) if sale_prices else None,
            "building_median_rent": int(sum(lease_rents) / len(lease_rents)) if lease_rents else None,
        },
        "public_housing_context": get_public_housing_context(address)
    }

def get_public_housing_context(address: str, gnaf_id: str = None) -> Dict[str, Any]:
    street_norm = normalize_street(address)
    conn = get_db_connection()
    cur = conn.cursor()

    is_public_housing = False
    confidence = 0
    if gnaf_id:
        cur.execute("SELECT confidence_score FROM public_housing WHERE gnaf_pid = ?", (gnaf_id,))
        row = cur.fetchone()
        if row:
            is_public_housing = True
            confidence = row["confidence_score"]

    cur.execute("SELECT COUNT(*) as count FROM public_housing WHERE street_norm = ?", (street_norm,))
    street_count = cur.fetchone()["count"]
    conn.close()

    return {
        "is_public_housing_building": is_public_housing,
        "building_confidence_score": confidence,
        "social_housing_units_on_street": street_count,
        "summary": (
            f"🚨 VERIFIED PUBLIC HOUSING: Address is marked as public housing (confidence: {confidence})"
            if is_public_housing else
            (f"⚠️ {street_count} Verified Public Housing Dwellings on this street" if street_count > 0 else "✅ No public housing dwellings on this street")
        )
    }
