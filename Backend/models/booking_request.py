from datetime import date
from typing import Optional, Any, List, Literal

from pydantic import BaseModel, Field, field_validator


class BookingRequest(BaseModel):
    listing_id: Optional[str] = None
    listing_address_requested: Optional[str] = None
    matched_listing_address: Optional[str] = None
    listing_url: Optional[str] = None

    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    preferred_date: Optional[date] = None
    preferred_time: Optional[str] = None
    message: Optional[str] = None

    virtual_tour: Optional[bool] = None
    awaiting_listing_confirmation: bool = False
    awaiting_final_booking_confirmation: bool = False
    booking_ready: bool = False

    notes: List[str] = Field(default_factory=list)

    @field_validator(
        "listing_id",
        "listing_address_requested",
        "matched_listing_address",
        "listing_url",
        "full_name",
        "email",
        "phone",
        "preferred_time",
        "message",
        mode="before",
    )
    @classmethod
    def normalize_optional_strings(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text if text else None

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return []


class BookingParseResult(BaseModel):
    wants_to_book: bool = False

    listing_address: Optional[str] = None

    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    preferred_date: Optional[date] = None
    preferred_time: Optional[str] = None
    virtual_tour: Optional[bool] = None
    message: Optional[str] = None


    confirmation: Optional[Literal["yes", "no"]] = None
    notes: List[str] = Field(default_factory=list)

    @field_validator(
        "listing_address",
        "full_name",
        "email",
        "phone",
        "preferred_time",
        "message",
        mode="before",
    )
    @classmethod
    def normalize_optional_strings(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text if text else None

    @field_validator("confirmation", mode="before")
    @classmethod
    def normalize_confirmation(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip().lower()
        if text in {"yes", "y"}:
            return "yes"
        if text in {"no", "n"}:
            return "no"
        return None

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return []