from datetime import date
from typing import Optional, List, Any

from pydantic import BaseModel, Field, field_validator


class Location(BaseModel):
    city: str = ""
    region_id: Optional[str] = None
    radius_km: Optional[float] = None
    neighborhoods: List[str] = Field(default_factory=list)

    @field_validator("city", mode="before")
    @classmethod
    def normalize_city(cls, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @field_validator("region_id", mode="before")
    @classmethod
    def normalize_region_id(cls, value: Any) -> Optional[str]:
        if value is None or str(value).strip() == "":
            return None
        return str(value).strip()

    @field_validator("radius_km", mode="before")
    @classmethod
    def normalize_radius_km(cls, value: Any) -> Optional[float]:
        if value is None or value == "":
            return None
        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip().lower().replace("km", "").strip()
        try:
            return float(text)
        except ValueError:
            return None

    @field_validator("neighborhoods", mode="before")
    @classmethod
    def normalize_neighborhoods(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            cleaned = []
            seen = set()
            for item in value:
                text = str(item).strip()
                if text and text.lower() not in seen:
                    cleaned.append(text)
                    seen.add(text.lower())
            return cleaned
        return []


class Price(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None
    currency: str = "CAD"

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: Any) -> str:
        if value is None or str(value).strip() == "":
            return "CAD"
        return str(value).strip().upper()

    @field_validator("min", "max", mode="before")
    @classmethod
    def normalize_price_fields(cls, value: Any) -> Optional[int]:
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


class HousingFilters(BaseModel):
    location: Location = Field(default_factory=Location)
    price: Price = Field(default_factory=Price)
    beds_min: Optional[int] = None
    beds_max: Optional[int] = None
    baths_min: Optional[float] = None
    baths_max: Optional[float] = None
    property_types: List[str] = Field(default_factory=list)
    must_have: List[str] = Field(default_factory=list)
    nice_to_have: List[str] = Field(default_factory=list)
    move_in: Optional[date] = None
    min_sqft: Optional[int] = None
    min_lot_size: Optional[int] = None
    notes: List[str] = Field(default_factory=list)

    @field_validator("beds_min", "beds_max", "min_sqft", "min_lot_size", mode="before")
    @classmethod
    def normalize_int_fields(cls, value: Any) -> Optional[int]:
        if value is None or value == "":
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)

        text = str(value).strip().lower()
        text = text.replace(",", "").replace("sqft", "").replace("sq. ft.", "").strip()

        if text.isdigit():
            return int(text)

        return None

    @field_validator("baths_min", "baths_max", mode="before")
    @classmethod
    def normalize_bath_fields(cls, value: Any) -> Optional[float]:
        if value is None or value == "":
            return None
        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip()
        try:
            return float(text)
        except ValueError:
            return None

    @field_validator("property_types", mode="before")
    @classmethod
    def normalize_property_types(cls, value: Any) -> List[str]:
        if value is None:
            return []

        mapping = {
            1: "house",
            2: "condo",
            3: "townhouse",
            4: "multi-family",
            5: "land",
            6: "other",
            7: "manufactured",
            8: "co-op",
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

        if isinstance(value, list):
            cleaned = []
            seen = set()

            for item in value:
                raw = str(item).strip().lower()
                normalized = mapping.get(item, mapping.get(raw, raw))
                if normalized and normalized not in seen:
                    cleaned.append(normalized)
                    seen.add(normalized)

            return cleaned

        return []

    @field_validator("must_have", "nice_to_have", mode="before")
    @classmethod
    def normalize_amenity_lists(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            return []

        mapping = {
            "laundry": "in_unit_laundry",
            "washer/dryer": "in_unit_laundry",
            "washer dryer": "in_unit_laundry",
            "in-unit laundry": "in_unit_laundry",
            "in unit laundry": "in_unit_laundry",
            "cat friendly": "cat_friendly",
            "cats allowed": "cat_friendly",
            "dog friendly": "dog_friendly",
            "dogs allowed": "dog_friendly",
            "parking": "parking",
            "gym": "gym",
            "air conditioning": "ac",
            "ac": "ac",
            "elevator": "elevator",
            "fireplace": "fireplace",
            "waterfront": "wf",
            "view": "view",
            "accessible": "accessible",
            "pets allowed": "pets_allowed",
            "washer/dryer hookup": "wd",
            "virtual tour": "virtual_tour",
            "pool": "pool",
            "garage": "garage",
        }

        cleaned = []
        seen = set()

        for item in value:
            text = str(item).strip().lower()
            if not text:
                continue

            normalized = mapping.get(text, text.replace(" ", "_").replace("-", "_"))
            if normalized not in seen:
                cleaned.append(normalized)
                seen.add(normalized)

        return cleaned

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return []

    @field_validator("move_in", mode="before")
    @classmethod
    def normalize_move_in(cls, value: Any) -> Any:
        if value is None or value == "":
            return None
        return value