from typing import Optional, List, Any

from pydantic import BaseModel, Field, field_validator


class HousingFilters(BaseModel):
    address_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    location_text: Optional[str] = None

    property_type: Optional[str] = None

    beds_min: Optional[int] = None
    baths_min: Optional[float] = None

    price_min: Optional[int] = None
    price_max: Optional[int] = None

    days_on_market_max: Optional[int] = None
    time_on_redfin: Optional[str] = None
    hoa_amount_max: Optional[int] = None

    notes: List[str] = Field(default_factory=list)

    @field_validator(
        "address_name",
        "city",
        "state",
        "zip",
        "location_text",
        "property_type",
        "time_on_redfin",
        mode="before",
    )
    @classmethod
    def normalize_optional_strings(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text if text else None

    @field_validator(
        "beds_min",
        "days_on_market_max",
        "price_min",
        "price_max",
        "hoa_amount_max",
        mode="before",
    )
    @classmethod
    def normalize_int_fields(cls, value: Any) -> Optional[int]:
        if value is None or value == "":
            return None

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(value)

        text = str(value).strip().lower()
        text = text.replace("$", "").replace(",", "").replace("bucks", "").strip()

        if text.isdigit():
            return int(text)

        return None

    @field_validator("baths_min", mode="before")
    @classmethod
    def normalize_baths_min(cls, value: Any) -> Optional[float]:
        if value is None or value == "":
            return None

        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip()
        try:
            return float(text)
        except ValueError:
            return None

    @field_validator("property_type", mode="before")
    @classmethod
    def normalize_property_type(cls, value: Any) -> Optional[str]:
        if value is None:
            return None

        mapping = {
            "1": "house",
            "2": "condo",
            "3": "townhouse",
            "4": "multi-family",
            "5": "land",
            "6": "other",
            "7": "manufactured",
            "8": "co-op",
            "house": "house",
            "condo": "condo",
            "townhouse": "townhouse",
            "multi-family": "multi-family",
            "multifamily": "multi-family",
            "land": "land",
            "other": "other",
            "manufactured": "manufactured",
            "co-op": "co-op",
            "coop": "co-op",
        }

        raw = str(value).strip().lower()
        return mapping.get(raw, raw)

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return []