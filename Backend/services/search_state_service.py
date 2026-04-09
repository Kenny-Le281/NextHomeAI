from models.housing_filters import HousingFilters


def has_required_info_service(filters: HousingFilters) -> bool:
    return (
        filters.city is not None
        and filters.price_max is not None
        and filters.beds_min is not None
    )


def get_missing_fields_service(filters: HousingFilters) -> list[str]:
    missing = []

    if filters.city is None:
        missing.append("city")

    if filters.price_max is None:
        missing.append("maximum price")

    if filters.beds_min is None:
        missing.append("minimum number of bedrooms")

    return missing