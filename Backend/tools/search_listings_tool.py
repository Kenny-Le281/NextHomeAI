from configs.supabase_client import supabase
from models.housing_filters import HousingFilters

PROPERTY_TYPE_MAP = {
    "house": 1,
    "condo": 2,
    "townhouse": 3,
    "multi-family": 4,
    "land": 5,
    "other": 6,
    "manufactured": 7,
    "co-op": 8,
}


def build_listings_query(filters: HousingFilters):
    query = supabase.table("listings").select("*")

    if filters.address_name is not None:
        query = query.ilike("address_name", f"%{filters.address_name}%")

    if filters.city is not None:
        query = query.eq("city", filters.city)

    if filters.state is not None:
        query = query.eq("state", filters.state)

    if filters.zip is not None:
        query = query.eq("zip", filters.zip)

    if filters.location_text is not None:
        query = query.ilike("location", f"%{filters.location_text}%")

    if filters.property_type is not None:
        code = PROPERTY_TYPE_MAP.get(filters.property_type)
        if code is not None:
            query = query.eq("property_type", code)

    if filters.beds_min is not None:
        query = query.gte("beds", filters.beds_min)

    if filters.baths_min is not None:
        query = query.gte("total_baths", filters.baths_min)

    if filters.price_min is not None:
        query = query.gte("price", filters.price_min)

    if filters.price_max is not None:
        query = query.lte("price", filters.price_max)

    if filters.days_on_market_max is not None:
        query = query.lte("days_on_market", filters.days_on_market_max)

    if filters.hoa_amount_max is not None:
        query = query.lte("hoa_amount", filters.hoa_amount_max)

    if filters.time_on_redfin is not None:
        query = query.ilike("time_on_redfin", f"%{filters.time_on_redfin}%")

    return query


def search_listings_tool(filters: HousingFilters, limit: int = 50):
    query = build_listings_query(filters)
    response = query.order("price", desc=False).limit(limit).execute()
    return response.data