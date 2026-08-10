from llm.openai_client import call_llm
from llm.prompts import (
    build_missing_info_response_prompt,
    build_completion_response_prompt,
    build_missing_booking_info_prompt,
    build_booking_completion_prompt,
    build_listings_summary_prompt,
)
from models.housing_filters import HousingFilters
from models.booking_request import BookingRequest


def generate_missing_info_reply_service(filters: HousingFilters, missing_fields: list[str]) -> str:
    prompt = build_missing_info_response_prompt(
        current_filters=filters.model_dump(mode="json"),
        missing_fields=missing_fields,
    )
    return call_llm(prompt).strip()


def generate_completion_reply_service(filters: HousingFilters) -> str:
    prompt = build_completion_response_prompt(
        current_filters=filters.model_dump(mode="json")
    )
    return call_llm(prompt).strip()


def generate_listings_summary_service(filters: HousingFilters, listings: list[dict]) -> str:
    prompt = build_listings_summary_prompt(
        current_filters=filters.model_dump(mode="json"),
        listings=listings,
    )
    return call_llm(prompt).strip()



def generate_missing_booking_reply_service(booking: BookingRequest, missing_fields: list[str]) -> str:
    prompt = build_missing_booking_info_prompt(
        current_booking=booking.model_dump(mode="json"),
        missing_fields=missing_fields,
    )
    return call_llm(prompt).strip()


def generate_booking_completion_reply_service(booking: BookingRequest) -> str:
    prompt = build_booking_completion_prompt(
        current_booking=booking.model_dump(mode="json")
    )
    return call_llm(prompt).strip()
