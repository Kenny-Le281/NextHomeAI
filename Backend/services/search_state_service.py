from typing import List
from models.housing_filters import HousingFilters


def has_required_info_service(filters: HousingFilters) -> bool:
    return (
        bool(filters.location.city.strip())
        and filters.price.max is not None
        and filters.beds_min is not None
    )


def get_missing_fields_service(filters: HousingFilters) -> List[str]:
    missing = []

    if not filters.location.city.strip():
        missing.append("city or area")

    if filters.price.max is None:
        missing.append("maximum price")

    if filters.beds_min is None:
        missing.append("minimum number of bedrooms")

    return missing