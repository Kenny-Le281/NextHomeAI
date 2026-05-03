from models.booking_request import BookingRequest, BookingParseResult


def merge_booking_request_service(current_booking: BookingRequest, parsed: BookingParseResult) -> BookingRequest:
    merged = current_booking.model_dump(mode="python")

    if parsed.listing_address is not None:
        merged["listing_address_requested"] = parsed.listing_address

    if parsed.full_name is not None:
        merged["full_name"] = parsed.full_name

    if parsed.email is not None:
        merged["email"] = parsed.email

    if parsed.phone is not None:
        merged["phone"] = parsed.phone

    if parsed.virtual_tour is not None:
        merged["virtual_tour"] = parsed.virtual_tour

    if parsed.preferred_date is not None:
        merged["preferred_date"] = parsed.preferred_date

    if parsed.preferred_time is not None:
        merged["preferred_time"] = parsed.preferred_time

    if parsed.message is not None:
        merged["message"] = parsed.message

    if parsed.notes:
        merged["notes"] = merged["notes"] + parsed.notes

    return BookingRequest.model_validate(merged)


def has_required_booking_info_service(booking: BookingRequest) -> bool:
    return (
        booking.listing_id is not None
        and booking.listing_url is not None
        and booking.full_name is not None
        and booking.email is not None
        and booking.phone is not None
        and booking.preferred_date is not None
        and booking.preferred_time is not None
        and booking.virtual_tour is not None
    )


def get_next_booking_question_type_service(booking: BookingRequest) -> str | None:
    if booking.listing_id is None or booking.listing_url is None:
        return "booking_address"

    if booking.full_name is None:
        return "booking_name"

    if booking.email is None:
        return "booking_email"

    if booking.phone is None:
        return "booking_phone"

    if booking.preferred_date is None:
        return "booking_date"
    
    if booking.preferred_time is None:
        return "booking_time"
    
    if booking.virtual_tour is None:
        return "booking_virtual"

    return None


def build_single_booking_question_service(question_type: str | None) -> str:
    if question_type == "booking_address":
        return "What property address would you like to book a tour for?"

    if question_type == "booking_name":
        return "What full name should I use for the booking request?"

    if question_type == "booking_email":
        return "What email address should I include?"

    if question_type == "booking_phone":
        return "What phone number should I use?"

    if question_type == "booking_date":
        return "What date would you prefer for the tour?"
    
    if question_type == "booking_time":
        return "What time would you prefer for the tour?"
    
    if question_type == "booking_virtual":
        return "Would you prefer a virtual tour or an in-person tour?"

    if question_type == "booking_confirmation":
        return "Please reply yes or no."

    if question_type == "booking_final_confirmation":
        return "I have all the booking details. Would you like me to proceed with submitting the showing request? Please reply yes or no."

    return "What information would you like to provide next for the booking?"


def _extract_listing_id(listing: dict) -> str | None:
    listing_id_value = listing.get("listing_id")
    if listing_id_value is None:
        listing_id_value = listing.get("property_id")

    if listing_id_value is None:
        return None

    return str(listing_id_value).strip()


def _extract_listing_url(listing: dict) -> str | None:
    raw_url = (
        listing.get("source_url")
        or listing.get("listing_url")
        or listing.get("url")
    )

    if not raw_url:
        return None

    raw_url = str(raw_url).strip()

    if raw_url.startswith("http://") or raw_url.startswith("https://"):
        return raw_url

    if raw_url.startswith("/"):
        return f"https://www.redfin.ca{raw_url}"

    return f"https://www.redfin.ca/{raw_url.lstrip('/')}"


def set_confirmed_listing_service(booking: BookingRequest, listing: dict) -> BookingRequest:
    updated = booking.model_dump(mode="python")
    updated["listing_id"] = _extract_listing_id(listing)
    updated["matched_listing_address"] = listing.get("address_name")
    updated["listing_url"] = _extract_listing_url(listing)
    updated["awaiting_listing_confirmation"] = False
    return BookingRequest.model_validate(updated)


def set_awaiting_listing_confirmation_service(booking: BookingRequest) -> BookingRequest:
    updated = booking.model_dump(mode="python")
    updated["awaiting_listing_confirmation"] = True
    return BookingRequest.model_validate(updated)


def clear_awaiting_listing_confirmation_service(booking: BookingRequest) -> BookingRequest:
    updated = booking.model_dump(mode="python")
    updated["awaiting_listing_confirmation"] = False
    return BookingRequest.model_validate(updated)


def set_awaiting_final_booking_confirmation_service(booking: BookingRequest) -> BookingRequest:
    updated = booking.model_dump(mode="python")
    updated["awaiting_final_booking_confirmation"] = True
    return BookingRequest.model_validate(updated)


def clear_awaiting_final_booking_confirmation_service(booking: BookingRequest) -> BookingRequest:
    updated = booking.model_dump(mode="python")
    updated["awaiting_final_booking_confirmation"] = False
    return BookingRequest.model_validate(updated)