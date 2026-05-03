import os
import sys
import psycopg2
import json
from dotenv import load_dotenv

# Load .env from repo root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from models.housing_filters import HousingFilters


def get_db_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres.uajcmeseaipjrplvndrp",
        password=os.getenv("SUPABASE_DB_PASSWORD"),
        host="aws-1-ca-central-1.pooler.supabase.com",
        port=5432,
        sslmode="require",
    )


def query_listings(filters: HousingFilters, limit: int = 20) -> list[dict]:
    """Build a SQL query from HousingFilters and return matching listings."""
    conditions = []
    params = []

    # City
    if filters.location.city.strip():
        conditions.append("LOWER(city) = LOWER(%s)")
        params.append(filters.location.city.strip())

    # Price
    if filters.price.min is not None:
        conditions.append("price >= %s")
        params.append(filters.price.min)
    if filters.price.max is not None:
        conditions.append("price <= %s")
        params.append(filters.price.max)

    # Beds
    if filters.beds_min is not None:
        conditions.append("beds >= %s")
        params.append(filters.beds_min)
    if filters.beds_max is not None:
        conditions.append("beds <= %s")
        params.append(filters.beds_max)

    # Baths
    if filters.baths_min is not None:
        conditions.append("total_baths >= %s")
        params.append(filters.baths_min)
    if filters.baths_max is not None:
        conditions.append("total_baths <= %s")
        params.append(filters.baths_max)

    # Property type — map semantic names to Redfin Canada's numeric codes
    if filters.property_types:
        type_map = {
            "house": 6,
            "condo": 3,
            "townhouse": 13,
            "multi-family": 4,
            "land": 8,
            "other": 10,
        }
        codes = [type_map[pt.lower()] for pt in filters.property_types if pt.lower() in type_map]
        if codes:
            placeholders = ", ".join(["%s"] * len(codes))
            conditions.append(f"property_type IN ({placeholders})")
            params.extend(codes)

    where_clause = " AND ".join(conditions) if conditions else "TRUE"

    sql = f"""
        SELECT listing_id, property_id, address_name, city, state, zip,
               url, property_type, beds, baths, price, total_baths,
               days_on_market, latitude, longitude, hoa_amount
        FROM listings
        WHERE {where_clause}
        ORDER BY price ASC
        LIMIT %s
    """
    params.append(limit)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(sql, params)

    columns = [desc[0] for desc in cur.description]
    results = []
    for row in cur.fetchall():
        record = {}
        for col, val in zip(columns, row):
            # Convert Decimal to float for JSON serialization
            if hasattr(val, 'as_tuple'):  # Decimal check
                record[col] = float(val)
            else:
                record[col] = val
        results.append(record)

    cur.close()
    conn.close()

    return results


def query_listing_by_address(address_query: str, limit: int = 10) -> list[dict]:
    if not address_query or not address_query.strip():
        return []

    sql = """
        SELECT listing_id, property_id, address_name, city, state, zip,
               url, property_type, beds, baths, price, total_baths,
               days_on_market, latitude, longitude, hoa_amount
        FROM listings
        WHERE address_name ILIKE %s
        ORDER BY price ASC
        LIMIT %s
    """

    params = [f"%{address_query.strip()}%", limit]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(sql, params)

    columns = [desc[0] for desc in cur.description]
    results = []

    for row in cur.fetchall():
        record = {}

        for col, val in zip(columns, row):
            if hasattr(val, "as_tuple"):
                record[col] = float(val)
            else:
                record[col] = val

        results.append(record)

    cur.close()
    conn.close()

    return results
