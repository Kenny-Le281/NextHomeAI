from models.housing_filters import HousingFilters


def merge_filters(old: HousingFilters, new: HousingFilters) -> HousingFilters:
    merged_data = old.model_dump(mode="python")

    if new.location.city.strip():
        merged_data["location"]["city"] = new.location.city

    if new.location.region_id:
        merged_data["location"]["region_id"] = new.location.region_id

    if new.location.radius_km is not None:
        merged_data["location"]["radius_km"] = new.location.radius_km

    if new.location.neighborhoods:
        existing = merged_data["location"]["neighborhoods"]
        combined = existing + new.location.neighborhoods
        deduped = []
        seen = set()
        for item in combined:
            key = item.lower()
            if key not in seen:
                deduped.append(item)
                seen.add(key)
        merged_data["location"]["neighborhoods"] = deduped

    if new.price.min is not None:
        merged_data["price"]["min"] = new.price.min

    if new.price.max is not None:
        merged_data["price"]["max"] = new.price.max

    if new.price.currency:
        merged_data["price"]["currency"] = new.price.currency

    if new.beds_min is not None:
        merged_data["beds_min"] = new.beds_min

    if new.beds_max is not None:
        merged_data["beds_max"] = new.beds_max

    if new.baths_min is not None:
        merged_data["baths_min"] = new.baths_min

    if new.baths_max is not None:
        merged_data["baths_max"] = new.baths_max

    if new.move_in is not None:
        merged_data["move_in"] = new.move_in

    if new.min_sqft is not None:
        merged_data["min_sqft"] = new.min_sqft

    if new.min_lot_size is not None:
        merged_data["min_lot_size"] = new.min_lot_size

    merged_data["property_types"] = sorted(list(set(merged_data["property_types"] + new.property_types)))

    merged_data["must_have"] = sorted(list(set(merged_data["must_have"] + new.must_have)))

    merged_data["nice_to_have"] = sorted(list(set(merged_data["nice_to_have"] + new.nice_to_have)))

    if new.notes:
        merged_data["notes"] = merged_data["notes"] + new.notes

    return HousingFilters.model_validate(merged_data)