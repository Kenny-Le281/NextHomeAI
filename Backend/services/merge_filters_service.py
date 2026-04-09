from models.housing_filters import HousingFilters


def merge_filters_service(old: HousingFilters, new: HousingFilters) -> HousingFilters:
    merged = old.model_dump(mode="python")

    if new.address_name is not None:
        merged["address_name"] = new.address_name

    if new.city is not None:
        merged["city"] = new.city

    if new.state is not None:
        merged["state"] = new.state

    if new.zip is not None:
        merged["zip"] = new.zip

    if new.location_text is not None:
        merged["location_text"] = new.location_text

    if new.property_type is not None:
        merged["property_type"] = new.property_type

    if new.beds_min is not None:
        merged["beds_min"] = new.beds_min

    if new.baths_min is not None:
        merged["baths_min"] = new.baths_min

    if new.price_min is not None:
        merged["price_min"] = new.price_min

    if new.price_max is not None:
        merged["price_max"] = new.price_max

    if new.days_on_market_max is not None:
        merged["days_on_market_max"] = new.days_on_market_max

    if new.time_on_redfin is not None:
        merged["time_on_redfin"] = new.time_on_redfin

    if new.hoa_amount_max is not None:
        merged["hoa_amount_max"] = new.hoa_amount_max

    if new.notes:
        merged["notes"] = merged["notes"] + new.notes

    return HousingFilters.model_validate(merged)