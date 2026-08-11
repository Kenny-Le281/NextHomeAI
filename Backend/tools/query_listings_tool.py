import json

from database import get_db_connection
from models.housing_filters import HousingFilters


def _rows_to_records(cursor) -> list[dict]:
    columns = [description[0] for description in cursor.description]
    results = []
    for row in cursor.fetchall():
        record = {}
        for column, value in zip(columns, row):
            if hasattr(value, "as_tuple"):
                record[column] = float(value)
            elif column == "image_urls" and isinstance(value, str):
                try:
                    record[column] = json.loads(value)
                except json.JSONDecodeError:
                    record[column] = []
            else:
                record[column] = value
        results.append(record)
    return results


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
               days_on_market, latitude, longitude, hoa_amount, last_sold_date, image_urls, sqft
        FROM listings
        WHERE {where_clause}
        ORDER BY price ASC
        LIMIT %s
    """
    params.append(limit)

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return _rows_to_records(cursor)
    finally:
        connection.close()


def query_listing_by_address(address_query: str, limit: int = 10) -> list[dict]:
    if not address_query or not address_query.strip():
        return []

    sql = """
        SELECT listing_id, property_id, address_name, city, state, zip,
               url, property_type, beds, baths, price, total_baths,
               days_on_market, latitude, longitude, hoa_amount, last_sold_date, image_urls, sqft
        FROM listings
        WHERE address_name ILIKE %s
        ORDER BY price ASC
        LIMIT %s
    """

    params = [f"%{address_query.strip()}%", limit]

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return _rows_to_records(cursor)
    finally:
        connection.close()
