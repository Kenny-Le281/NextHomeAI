from models.housing_filters import HousingFilters
from models.session_context import SessionContext
from tools.classify_intent_tool import classify_intent_tool
from tools.query_listings_tool import query_listings
from services.merge_filters_service import merge_filters_service
from tools.normal_chat_tool import normal_chat_tool
from tools.parse_filters_tool import parse_filters_tool
from services.response_generation_service import (
    generate_completion_reply_service,
    generate_missing_info_reply_service,
    generate_listings_summary_service,
)
from services.search_state_service import has_required_info, get_missing_fields
from tools.search_listings_tool import search_listings_tool


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


def _question_type_from_missing_fields(missing_fields: list[str]) -> str | None:
    if not missing_fields:
        return None

    first = missing_fields[0]

    if first == "city":
        return "city"

    if first == "maximum price":
        return "price_max"

    if first == "minimum number of bedrooms":
        return "beds_min"

    return None


def _copy_context(context: SessionContext) -> SessionContext:
    return SessionContext.model_validate(context.model_dump(mode="python"))



def run_agent(
    user_input: str,
    current_filters: HousingFilters,
    current_context: SessionContext,
) -> dict:
    """
    Main orchestration layer.

    Returns a dict with:
    - reply
    - filters
    - context
    - done
    - intent
    - listings
    """

    updated_context = _copy_context(current_context)
    intent_result = classify_intent_tool(
        user_message=user_input,
        current_filters=current_filters.model_dump(mode="json"),
    )

    intent = intent_result.intent

    if intent == "end_chat":
        updated_context.active_flow = None
        updated_context.last_question_type = None

        return {
            "reply": "Okay, ending the chat.",
            "filters": current_filters,
            "context": updated_context,
            "done": True,
            "api_params": None,
            "intent": intent,
            "listings": None,
        }

    if intent in {"general_question", "conversation"}:
        reply = normal_chat_tool(
            user_message=user_input,
            current_filters=current_filters.model_dump(mode="json")
        )

        return {
            "reply": reply,
            "filters": current_filters,
            "context": updated_context,
            "done": False,
            "api_params": None,
            "intent": intent,
            "listings": None,
        }

    if intent in {"provide_search_info", "refine_search"}:
        parsed_filters = parse_filters_tool(
            user_query=user_input,
            current_filters=current_filters.model_dump(mode="json"),
            current_context=updated_context.model_dump(mode="json"),
        )

        updated_filters = merge_filters_service(current_filters, parsed_filters)

        if has_required_info(updated_filters):
            reply = generate_completion_reply_service(updated_filters)
            api_params = build_api_params_tool(updated_filters)
            return {
                "reply": reply,
                "filters": updated_filters,
                "done": True,
                "api_params": api_params,
                "intent": intent,
            }

        missing_fields = get_missing_fields_service(updated_filters)
        updated_context.last_question_type = _question_type_from_missing_fields(missing_fields)

        reply = generate_missing_info_reply_service(updated_filters, missing_fields)

        return {
            "reply": reply,
            "filters": updated_filters,
            "context": updated_context,
            "done": False,
            "api_params": None,
            "intent": intent,
            "listings": None,
        }

    if intent == "confirm_search":
        if has_required_info(current_filters):
            reply = generate_completion_reply_service(current_filters)
            api_params = build_api_params_tool(current_filters)
            return {
                "reply": reply,
                "filters": current_filters,
                "done": True,
                "api_params": api_params,
                "intent": intent,
            }

        missing_fields = get_missing_fields_service(current_filters)
        updated_context.last_question_type = _question_type_from_missing_fields(missing_fields)

        reply = generate_missing_info_reply_service(current_filters, missing_fields)

        return {
            "reply": reply,
            "filters": current_filters,
            "context": updated_context,
            "done": False,
            "api_params": None,
            "intent": intent,
            "listings": None,
        }

    reply = normal_chat_tool(
        user_message=user_input,
        current_filters=current_filters.model_dump(mode="json")
    )

    return {
        "reply": reply,
        "filters": current_filters,
        "context": updated_context,
        "done": False,
        "api_params": None,
        "intent": intent,
        "listings": None,
    }
