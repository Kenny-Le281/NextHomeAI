import json


def build_filter_parser_prompt(
    user_query: str,
    current_filters: dict,
    current_context: dict,
) -> str:
    recent_history = current_context.get("conversation_history", [])[-8:]
    active_flow = current_context.get("active_flow")
    last_question_type = current_context.get("last_question_type")

    schema_example = {
        "address_name": None,
        "city": None,
        "state": None,
        "zip": None,
        "location_text": None,
        "property_type": None,
        "beds_min": None,
        "baths_min": None,
        "price_min": None,
        "price_max": None,
        "days_on_market_max": None,
        "time_on_redfin": None,
        "hoa_amount_max": None,
        "notes": []
    }

    return f"""
You are a real estate search filter parser.

Convert the user's latest message into VALID JSON only.

Recent conversation history:
{json.dumps(recent_history, indent=2)}

Current search filters:
{json.dumps(current_filters, indent=2)}

Current flow:
{json.dumps(active_flow)}

Last question type asked by the assistant:
{json.dumps(last_question_type)}

Rules:
- Return valid JSON only.
- Do not include markdown.
- Do not include triple backticks.
- Do not include comments.
- Do not include explanations.
- Use exactly this schema:
{json.dumps(schema_example, indent=2)}

Important:
- Use the recent conversation and last_question_type to interpret short replies.
- If the assistant was asking for city and the user says "Ottawa", set city="Ottawa".
- If the assistant was asking for maximum price and the user says "600000", set price_max=600000.
- If the assistant was asking for bedrooms and the user says "3", set beds_min=3.
- Leave unknown values as null.
- Do not invent fields.

User message:
{user_query}
""".strip()


def build_booking_parser_prompt(
    user_message: str,
    current_booking: dict,
    current_context: dict,
) -> str:
    recent_history = current_context.get("conversation_history", [])[-8:]
    last_question_type = current_context.get("last_question_type")
    latest_listings = current_context.get("latest_listings", [])[:10]

    schema_example = {
        "wants_to_book": True,
        "listing_address": None,
        "full_name": None,
        "email": None,
        "phone": None,
        "preferred_date": None,
        "preferred_time": None,
        "virtual_tour": None,
        "message": None,
        "confirmation": None,
        "notes": []
    }

    return f"""
You are a booking-intake parser for a real estate chatbot.

Convert the user's latest message into VALID JSON only.

Recent conversation history:
{json.dumps(recent_history, indent=2)}

Current booking state:
{json.dumps(current_booking, indent=2)}

Last question type:
{json.dumps(last_question_type)}

Most recent listings shown to the user:
{json.dumps(latest_listings, indent=2)}

Rules:
- Return valid JSON only.
- Do not include markdown.
- Do not include triple backticks.
- Do not include comments.
- Do not include explanations.
- Use exactly this schema:
{json.dumps(schema_example, indent=2)}

Field meanings:
- wants_to_book: true if the user is trying to book/request a tour
- listing_address: property address mentioned by the user
- full_name: user's full name if provided
- email: user's email if provided
- phone: user's phone number if provided
- preferred_date: convert to YYYY-MM-DD format
- preferred_time: must only be a real clock time, such as "1:00 pm", "1:30 pm", "15:30", or "9 am".
- Do not set preferred_time from phrases like "in person", "virtual", "video tour", "showing", "tour", "morning", "afternoon", or "evening".
- If the user does not give a specific clock time, set preferred_time to null.
- "in person" means virtual_tour=false. It is not a preferred_time.
- message: optional message for the agent
- confirmation: "yes" or "no" only if the user is clearly confirming or rejecting a suggested listing or final booking submission
- notes: use only if something important is ambiguous

Important:
- Use conversation history and last_question_type to interpret short replies.
- If last_question_type is "booking_name" and the user gives a short person name, set full_name.
- If last_question_type is "booking_email" and the user gives an email, set email.
- If last_question_type is "booking_phone" and the user gives a phone number, set phone.
- If last_question_type is "booking_date" and the user gives a date, set preferred_date.
- If last_question_type is "booking_time" and the user gives a valid clock time, set preferred_time. If they do not give a valid clock time, leave preferred_time as null.
- virtual_tour: true only if the user clearly asks for a virtual/video/online tour
- virtual_tour: false only if the user clearly asks for an in-person tour/showing
- virtual_tour: null if the user has not specified the tour type
- If last_question_type is "booking_virtual" and the user says virtual/video/online, set virtual_tour=true.
- If last_question_type is "booking_virtual" and the user says in-person/showing, set virtual_tour=false.
- If last_question_type is "booking_confirmation" or "booking_final_confirmation" and the user says yes or no, set confirmation.
- If last_question_type is "booking_address" and the user gives an address, set listing_address.
- If the user changes a previously given booking detail, return the updated value in the appropriate field.
- Do not invent details.

User message:
{user_message}
""".strip()


def build_intent_classifier_prompt(
    user_message: str,
    current_filters: dict,
    current_context: dict,
    current_booking: dict,
) -> str:
    recent_history = current_context.get("conversation_history", [])[-8:]
    active_flow = current_context.get("active_flow")
    last_question_type = current_context.get("last_question_type")

    schema_example = {
        "intent": "provide_search_info",
        "reason": "The user is giving property requirements."
    }

    return f"""
You are an intent classifier for a real estate chatbot.

Classify the user's latest message into exactly one of these intents:

- provide_search_info
- refine_search
- general_question
- conversation
- confirm_search
- start_booking
- provide_booking_info
- confirm_booking
- end_chat

Recent conversation history:
{json.dumps(recent_history, indent=2)}

Current search filters:
{json.dumps(current_filters, indent=2)}

Current booking state:
{json.dumps(current_booking, indent=2)}

Current flow:
{json.dumps(active_flow)}

Last question type:
{json.dumps(last_question_type)}

User message:
{user_message}

Intent guidance:
- provide_search_info: user gives initial property requirements
- refine_search: user changes or adds search requirements
- general_question: user asks a question that should be answered conversationally
- conversation: greeting or casual non-search chat
- confirm_search: user confirms the current search or asks to proceed
- start_booking: user starts asking to book a tour/showing for a property
- provide_booking_info: user provides booking details like address, name, email, phone, date, time, message
- confirm_booking: user confirms or rejects a suggested booking/listing match or confirms final booking submission
- end_chat: user wants to stop

Important:
- Use recent history and current flow to interpret short replies.
- If current flow is booking and last_question_type is one of booking_name, booking_email, booking_phone, booking_date, booking_address, booking_confirmation, booking_final_confirmation, then short direct answers should usually be classified as provide_booking_info or confirm_booking, not search.
- If the assistant asked for booking confirmation or final booking confirmation and the user says yes/no, use confirm_booking.
- If the user says "book a tour for ..." use start_booking.

Rules:
- Return valid JSON only.
- Do not include markdown.
- Do not include triple backticks.
- Do not include comments.
- Use exactly this schema:
{json.dumps(schema_example, indent=2)}
""".strip()


def build_normal_chat_prompt(
    user_message: str,
    current_filters: dict,
    current_context: dict,
    current_booking: dict,
) -> str:
    recent_history = current_context.get("conversation_history", [])[-8:]
    active_flow = current_context.get("active_flow")
    last_question_type = current_context.get("last_question_type")

    return f"""
You are a helpful real estate chatbot.

Recent conversation history:
{json.dumps(recent_history, indent=2)}

Current search filters:
{json.dumps(current_filters, indent=2)}

Current booking state:
{json.dumps(current_booking, indent=2)}

Current flow:
{json.dumps(active_flow)}

Last question type:
{json.dumps(last_question_type)}

User message:
{user_message}

Instructions:
- Respond naturally and conversationally.
- Use the recent conversation as context.
- Do not pretend to have searched listings unless results were actually returned.
- Do not modify state.
- Keep the reply concise and useful.
- Do not use bullet points.

Return only plain text.
""".strip()


def build_missing_info_response_prompt(current_filters: dict, missing_fields: list[str]) -> str:
    return f"""
You are a helpful real estate search assistant.

Current parsed filters:
{json.dumps(current_filters, indent=2)}

Missing required fields:
{json.dumps(missing_fields, indent=2)}

Instructions:
- Write a short natural reply.
- Ask only for the missing required information.
- Keep it conversational and concise.
- Do not use bullet points.

Return only plain text.
""".strip()


def build_completion_response_prompt(current_filters: dict) -> str:
    return f"""
You are a helpful real estate search assistant.

Current parsed filters:
{json.dumps(current_filters, indent=2)}

Instructions:
- Write a short natural reply confirming that enough information has been collected.
- Briefly summarize the most important preferences.
- Keep it conversational and concise.
- Do not use bullet points.

Return only plain text.
""".strip()


def build_booking_completion_prompt(current_booking: dict) -> str:
    return f"""
You are a helpful real estate booking assistant.

Current booking state:
{json.dumps(current_booking, indent=2)}

Instructions:
- Write a short natural reply confirming that enough information has been collected to prepare the booking request.
- Briefly summarize the booking details.
- Keep it conversational and concise.
- Do not use bullet points.

Return only plain text.
""".strip()


def build_missing_booking_info_prompt(current_booking: dict, missing_fields: list[str]) -> str:
    return f"""
You are a helpful real estate booking assistant.

Current booking state:
{json.dumps(current_booking, indent=2)}

Missing required booking fields:
{json.dumps(missing_fields, indent=2)}

Instructions:
- Write a short natural reply.
- Ask only for the missing booking information.
- Keep it conversational and concise.
- Do not use bullet points.

Return only plain text.
""".strip()