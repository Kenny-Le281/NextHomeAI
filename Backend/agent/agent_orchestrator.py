from models.housing_filters import HousingFilters
from models.booking_request import BookingRequest
from models.session_context import SessionContext

from tools.classify_intent_tool import classify_intent_tool
from tools.normal_chat_tool import normal_chat_tool
from tools.parse_filters_tool import parse_filters_tool
from tools.parse_booking_request_tool import parse_booking_request_tool
from tools.book_showing_tool import book_showing_tool

from tools.build_api_params_tool import build_api_params_tool
from tools.query_listings_tool import query_listings

from services.merge_filters_service import merge_filters_service
from services.response_generation_service import (
    generate_completion_reply_service,
    generate_missing_info_reply_service,
    generate_booking_completion_reply_service,
    generate_listings_summary_service,
)
from services.search_state_service import (
    has_required_info_service,
    get_missing_fields_service,
)
from services.booking_state_service import (
    merge_booking_request_service,
    has_required_booking_info_service,
    set_confirmed_listing_service,
    set_awaiting_listing_confirmation_service,
    clear_awaiting_listing_confirmation_service,
    get_next_booking_question_type_service,
    build_single_booking_question_service,
    set_awaiting_final_booking_confirmation_service,
    clear_awaiting_final_booking_confirmation_service,
)
from services.listing_selection_service import find_listing_for_booking_service


def _question_type_from_missing_search_fields(missing_fields: list[str]) -> str | None:
    if not missing_fields:
        return None

    first = missing_fields[0]

    if first == "city or area":
        return "city"

    if first == "maximum price":
        return "price_max"

    if first == "minimum number of bedrooms":
        return "beds_min"

    return None


def _copy_context(context: SessionContext) -> SessionContext:
    return SessionContext.model_validate(context.model_dump(mode="python"))


def _copy_booking(booking: BookingRequest) -> BookingRequest:
    return BookingRequest.model_validate(booking.model_dump(mode="python"))


def _override_intent_for_booking_followup(
    raw_intent: str,
    user_input: str,
    current_context: SessionContext,
) -> str:
    if current_context.active_flow != "booking":
        return raw_intent

    if current_context.last_question_type in {"booking_confirmation", "booking_final_confirmation"}:
        lowered = user_input.strip().lower()
        if lowered in {"yes", "y", "no", "n"}:
            return "confirm_booking"

    if current_context.last_question_type in {
        "booking_address",
        "booking_name",
        "booking_email",
        "booking_phone",
        "booking_date",
        "booking_time",
        "booking_virtual",
    }:
        if raw_intent in {"provide_search_info", "refine_search", "conversation", "general_question"}:
            return "provide_booking_info"

    return raw_intent


def _search_and_respond(
    filters: HousingFilters,
    context: SessionContext,
    booking: BookingRequest,
    intent: str,
) -> dict:
    """
    Query the DB with the collected filters and build a response.
    Also stores the returned listings in context.latest_listings so the booking
    flow can match addresses against the listings the user most recently saw.
    """
    listings = query_listings(filters)
    api_params = build_api_params_tool(filters)

    context.active_flow = "search"
    context.latest_listings = listings
    context.last_question_type = None

    if listings:
        reply = generate_listings_summary_service(filters, listings)
    else:
        reply = generate_completion_reply_service(filters)
        reply += (
            "\n\nI couldn't find any listings matching those criteria. "
            "You might want to try increasing your budget, changing the property type, "
            "or broadening the location."
        )

    return {
        "reply": reply,
        "filters": filters,
        "context": context,
        "booking": booking,
        "done": False,
        "api_params": api_params,
        "listings": listings,
        "intent": intent,
    }


def _missing_search_info_response(
    filters: HousingFilters,
    context: SessionContext,
    booking: BookingRequest,
    intent: str,
) -> dict:
    missing_fields = get_missing_fields_service(filters)
    context.last_question_type = _question_type_from_missing_search_fields(missing_fields)

    reply = generate_missing_info_reply_service(filters, missing_fields)

    return {
        "reply": reply,
        "filters": filters,
        "context": context,
        "booking": booking,
        "done": False,
        "api_params": None,
        "listings": None,
        "intent": intent,
    }


def run_agent(
    user_input: str,
    current_filters: HousingFilters,
    current_context: SessionContext,
    current_booking: BookingRequest,
) -> dict:
    updated_context = _copy_context(current_context)
    updated_booking = _copy_booking(current_booking)

    intent_result = classify_intent_tool(
        user_message=user_input,
        current_filters=current_filters.model_dump(mode="json"),
        current_context=updated_context.model_dump(mode="json"),
        current_booking=updated_booking.model_dump(mode="json"),
    )

    intent = _override_intent_for_booking_followup(
        raw_intent=intent_result.intent,
        user_input=user_input,
        current_context=updated_context,
    )

    if intent == "end_chat":
        updated_context.active_flow = None
        updated_context.last_question_type = None

        return {
            "reply": "Okay, ending the chat.",
            "filters": current_filters,
            "context": updated_context,
            "booking": updated_booking,
            "done": True,
            "api_params": None,
            "listings": None,
            "intent": intent,
        }

    if intent in {"general_question", "conversation"}:
        reply = normal_chat_tool(
            user_message=user_input,
            current_filters=current_filters.model_dump(mode="json"),
            current_context=updated_context.model_dump(mode="json"),
            current_booking=updated_booking.model_dump(mode="json"),
        )

        return {
            "reply": reply,
            "filters": current_filters,
            "context": updated_context,
            "booking": updated_booking,
            "done": False,
            "api_params": None,
            "listings": None,
            "intent": intent,
        }

    if intent in {"provide_search_info", "refine_search"}:
        parsed_filters = parse_filters_tool(
            user_query=user_input,
            current_filters=current_filters.model_dump(mode="json"),
            current_context=updated_context.model_dump(mode="json"),
        )

        updated_filters = merge_filters_service(current_filters, parsed_filters)
        updated_context.active_flow = "search"

        if has_required_info_service(updated_filters):
            return _search_and_respond(
                filters=updated_filters,
                context=updated_context,
                booking=updated_booking,
                intent=intent,
            )

        return _missing_search_info_response(
            filters=updated_filters,
            context=updated_context,
            booking=updated_booking,
            intent=intent,
        )

    if intent == "confirm_search":
        updated_context.active_flow = "search"

        if has_required_info_service(current_filters):
            return _search_and_respond(
                filters=current_filters,
                context=updated_context,
                booking=updated_booking,
                intent=intent,
            )

        return _missing_search_info_response(
            filters=current_filters,
            context=updated_context,
            booking=updated_booking,
            intent=intent,
        )

    if intent in {"start_booking", "provide_booking_info", "confirm_booking"}:
        updated_context.active_flow = "booking"

        parsed_booking = parse_booking_request_tool(
            user_message=user_input,
            current_booking=updated_booking.model_dump(mode="json"),
            current_context=updated_context.model_dump(mode="json"),
        )

        updated_booking = merge_booking_request_service(updated_booking, parsed_booking)

        # Final booking confirmation yes/no
        if updated_booking.awaiting_final_booking_confirmation and parsed_booking.confirmation is not None:
            if parsed_booking.confirmation == "yes":
                updated_booking = clear_awaiting_final_booking_confirmation_service(updated_booking)

                booking_result = book_showing_tool(updated_booking)
                updated_booking.booking_ready = True
                updated_context.last_question_type = None

                reply = generate_booking_completion_reply_service(updated_booking)
                reply = f"{reply}\n\nBooking tool result: {booking_result['message']}"

                return {
                    "reply": reply,
                    "filters": current_filters,
                    "context": updated_context,
                    "booking": updated_booking,
                    "done": False,
                    "api_params": None,
                    "listings": None,
                    "intent": intent,
                }

            if parsed_booking.confirmation == "no":
                updated_booking = clear_awaiting_final_booking_confirmation_service(updated_booking)
                updated_context.last_question_type = None

                return {
                    "reply": "Okay. I have not submitted the showing request.",
                    "filters": current_filters,
                    "context": updated_context,
                    "booking": updated_booking,
                    "done": False,
                    "api_params": None,
                    "listings": None,
                    "intent": intent,
                }

        # Address confirmation yes/no
        if updated_booking.awaiting_listing_confirmation and parsed_booking.confirmation is not None:
            if parsed_booking.confirmation == "yes":
                match_result = find_listing_for_booking_service(
                    updated_booking.listing_address_requested,
                    updated_context.latest_listings,
                )

                if match_result["listing"] is not None:
                    updated_booking = set_confirmed_listing_service(
                        updated_booking,
                        match_result["listing"],
                    )
                    updated_context.last_question_type = None

            elif parsed_booking.confirmation == "no":
                updated_booking = clear_awaiting_listing_confirmation_service(updated_booking)
                updated_context.last_question_type = "booking_address"

                return {
                    "reply": build_single_booking_question_service("booking_address"),
                    "filters": current_filters,
                    "context": updated_context,
                    "booking": updated_booking,
                    "done": False,
                    "api_params": None,
                    "listings": None,
                    "intent": intent,
                }

        # Resolve listing if address is provided but listing not yet confirmed
        if updated_booking.listing_id is None and updated_booking.listing_address_requested is not None:
            match_result = find_listing_for_booking_service(
                updated_booking.listing_address_requested,
                updated_context.latest_listings,
            )

            if match_result["status"] == "exact":
                updated_booking = set_confirmed_listing_service(
                    updated_booking,
                    match_result["listing"],
                )

            elif match_result["status"] == "candidate":
                candidate = match_result["listing"]

                updated_booking = set_awaiting_listing_confirmation_service(updated_booking)
                updated_context.last_question_type = "booking_confirmation"

                reply = (
                    "I couldn't find an exact match in the listings I most recently showed you. "
                    f"Did you mean {candidate['address_name']}? Please reply yes or no."
                )

                return {
                    "reply": reply,
                    "filters": current_filters,
                    "context": updated_context,
                    "booking": updated_booking,
                    "done": False,
                    "api_params": None,
                    "listings": None,
                    "intent": intent,
                }

            else:
                updated_context.last_question_type = "booking_address"

                return {
                    "reply": (
                        "I couldn't match that address in the listings I most recently showed you. "
                        "Please give the full property address, or search for the listing again first."
                    ),
                    "filters": current_filters,
                    "context": updated_context,
                    "booking": updated_booking,
                    "done": False,
                    "api_params": None,
                    "listings": None,
                    "intent": intent,
                }

        # If all booking info is ready, ask for final confirmation instead of submitting immediately
        if has_required_booking_info_service(updated_booking):
            updated_booking = set_awaiting_final_booking_confirmation_service(updated_booking)
            updated_context.last_question_type = "booking_final_confirmation"

            reply = (
                "I have everything I need to submit the showing request for "
                f"{updated_booking.matched_listing_address or updated_booking.listing_address_requested}. "
                "Would you like me to proceed? Please reply yes or no."
            )

            return {
                "reply": reply,
                "filters": current_filters,
                "context": updated_context,
                "booking": updated_booking,
                "done": False,
                "api_params": None,
                "listings": None,
                "intent": intent,
            }

        next_question_type = get_next_booking_question_type_service(updated_booking)
        updated_context.last_question_type = next_question_type

        reply = build_single_booking_question_service(next_question_type)

        return {
            "reply": reply,
            "filters": current_filters,
            "context": updated_context,
            "booking": updated_booking,
            "done": False,
            "api_params": None,
            "listings": None,
            "intent": intent,
        }

    reply = normal_chat_tool(
        user_message=user_input,
        current_filters=current_filters.model_dump(mode="json"),
        current_context=updated_context.model_dump(mode="json"),
        current_booking=updated_booking.model_dump(mode="json"),
    )

    return {
        "reply": reply,
        "filters": current_filters,
        "context": updated_context,
        "booking": updated_booking,
        "done": False,
        "api_params": None,
        "listings": None,
        "intent": intent,
    }