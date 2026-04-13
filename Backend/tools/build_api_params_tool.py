from models.housing_filters import HousingFilters


def _format_min_max(min_value, max_value) -> str | None:
    if min_value is not None and max_value is not None:
        return f"{min_value},{max_value}"
    if min_value is not None:
        return f"{min_value}"
    if max_value is not None:
        return f",{max_value}"
    return None


def _format_baths(value: float | None) -> str | None:
    if value is None:
        return None
    text = str(value)
    if text.endswith(".0"):
        return text[:-2]
    return text


def build_api_params_tool(filters: HousingFilters) -> dict:
    type_map = {
        "house": "6",
        "condo": "3",
        "townhouse": "13",
        "multi-family": "4",
        "land": "8",
        "other": "10",
    }

    boolean_filter_map = {
        "ac": "ac",
        "fireplace": "fireplace",
        "elevator": "elevator",
        "accessible": "accessible",
        "pets_allowed": "pets_allowed",
        "wd": "wd",
        "virtual_tour": "virtual_tour",
        "wf": "wf",
        "view": "view",
    }

    api_params = {
        "regionId": filters.location.region_id,
        "sort": None,
        "limit": 350,
        "page": 1,
        "prices": _format_min_max(filters.price.min, filters.price.max),
        "beds": filters.beds_min,
        "baths": _format_baths(filters.baths_min),
        "homeType": None,
        "squareFeet": _format_min_max(filters.min_sqft, None),
        "lotSize": _format_min_max(filters.min_lot_size, None),
        "status": 9,
        "timeOnRedfin": "-",
        "stories": None,
        "yearBuilt": None,
        "booleanFilters": [],
        "pool": None,
        "garageSpots": None,
        "hoaFees": None,
        "priceSqft": None,
        "propertyTaxes": None,
        "acceptedFinancing": None,
        "priceReduced": None,
        "listingType": None,
        "greatSchoolsRating": None,
        "schoolTypes": [],
        "walkScore": None,
        "transitScore": None,
        "bikeScore": None,
        "openHouse": None,
        "keyword": None,
    }

    mapped_types = []
    for t in filters.property_types:
        if t in type_map:
            mapped_types.append(type_map[t])
    if mapped_types:
        api_params["homeType"] = ",".join(mapped_types)

    bools = []
    combined = filters.must_have + filters.nice_to_have
    for item in combined:
        mapped = boolean_filter_map.get(item)
        if mapped and mapped not in bools:
            bools.append(mapped)

    api_params["booleanFilters"] = bools

    if "pool" in filters.must_have:
        api_params["pool"] = 3

    if "garage" in filters.must_have or "garage" in filters.nice_to_have:
        api_params["garageSpots"] = 1

    return api_params
