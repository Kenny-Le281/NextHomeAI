from models.housing_filters import HousingFilters
from tools.build_api_params_tool import build_api_params_tool
from tools.classify_intent_tool import classify_intent_tool
from tools.query_listings_tool import query_listings
from services.merge_filters_service import merge_filters
from tools.normal_chat_tool import normal_chat_tool
from tools.parse_filters_tool import parse_filters_tool
from services.response_generation_service import (
    generate_completion_reply_service,
    generate_missing_info_reply_service,
    generate_listings_summary_service,
)
from services.search_state_service import has_required_info, get_missing_fields


def _search_and_respond(filters: HousingFilters) -> dict:
    """Query the DB with the collected filters and build a response."""
    listings = query_listings(filters)
    api_params = build_api_params_tool(filters)

    if listings:
        reply = generate_listings_summary_service(filters, listings)
    else:
        reply = generate_completion_reply_service(filters)
        reply += "\n\nI couldn't find any listings matching those criteria. You might want to try broadening your search."

    return {
        "reply": reply,
        "filters": filters,
        "done": True,
        "api_params": api_params,
        "listings": listings,
        "intent": "search_complete",
    }


def run_agent(user_input: str, current_filters: HousingFilters) -> dict:
    intent_result = classify_intent_tool(
        user_message=user_input,
        current_filters=current_filters.model_dump(mode="json"),
    )

    intent = intent_result.intent

    if intent == "end_chat":
        return {
            "reply": "Okay, ending the chat.",
            "filters": current_filters,
            "done": True,
            "api_params": None,
            "listings": None,
            "intent": intent,
        }

    if intent in {"general_question", "conversation"}:
        reply = normal_chat_tool(
            user_message=user_input,
            current_filters=current_filters.model_dump(mode="json"),
        )
        return {
            "reply": reply,
            "filters": current_filters,
            "done": False,
            "api_params": None,
            "listings": None,
            "intent": intent,
        }

    if intent in {"provide_search_info", "refine_search"}:
        parsed_filters = parse_filters_tool(user_input)
        updated_filters = merge_filters(current_filters, parsed_filters)

        if has_required_info(updated_filters):
            return _search_and_respond(updated_filters)

        missing_fields = get_missing_fields(updated_filters)
        reply = generate_missing_info_reply_service(updated_filters, missing_fields)

        return {
            "reply": reply,
            "filters": updated_filters,
            "done": False,
            "api_params": None,
            "listings": None,
            "intent": intent,
        }

    if intent == "confirm_search":
        if has_required_info(current_filters):
            return _search_and_respond(current_filters)

        missing_fields = get_missing_fields(current_filters)
        reply = generate_missing_info_reply_service(current_filters, missing_fields)
        return {
            "reply": reply,
            "filters": current_filters,
            "done": False,
            "api_params": None,
            "listings": None,
            "intent": intent,
        }

    reply = normal_chat_tool(
        user_message=user_input,
        current_filters=current_filters.model_dump(mode="json"),
    )
    return {
        "reply": reply,
        "filters": current_filters,
        "done": False,
        "api_params": None,
        "listings": None,
        "intent": intent,
    }
