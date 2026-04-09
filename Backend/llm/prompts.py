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

Field meanings:
- address_name: a full or partial address if the user gives one
- city: city name
- state: state/province code or name if given
- zip: postal/zip code if given
- location_text: neighborhood or area text such as "Kanata", "downtown", "Orleans"
- property_type: one of "house", "condo", "townhouse", "multi-family", "land", "other", "manufactured", "co-op"
- beds_min: minimum number of bedrooms
- baths_min: minimum number of bathrooms
- price_min: minimum price
- price_max: maximum price
- days_on_market_max: maximum days on market if the user mentions freshness
- time_on_redfin: short text if the user mentions it
- hoa_amount_max: maximum HOA amount if the user mentions it
- notes: use only if something important is unclear

Important:
- Use the recent conversation and last_question_type to interpret short replies.
- If the user gives a short answer like "Ottawa" and the assistant was asking for city, set city="Ottawa".
- If the user gives a short answer like "600000" and the assistant was asking for maximum price, set price_max=600000.
- If the user gives a short answer like "3" and the assistant was asking for minimum bedrooms, set beds_min=3.
- Leave unknown values as null.
- Do not invent fields.

User message:
{user_query}
""".strip()


def build_intent_classifier_prompt(
    user_message: str,
    current_filters: dict,
    current_context: dict,
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
- end_chat

Recent conversation history:
{json.dumps(recent_history, indent=2)}

Current search filters:
{json.dumps(current_filters, indent=2)}

Current flow:
{json.dumps(active_flow)}

Last question type asked by the assistant:
{json.dumps(last_question_type)}

User message:
{user_message}

Intent guidance:
- provide_search_info: user gives initial property requirements
- refine_search: user changes or adds search requirements
- general_question: user asks a question that should be answered conversationally
- conversation: greeting / casual non-search chat
- confirm_search: user confirms the search or asks to proceed
- end_chat: user wants to stop

Important:
- Use recent history and the current flow to interpret short replies.
- If the assistant just asked for city, price, or bedrooms, and the user gives a short direct answer, treat it as provide_search_info.
- If the user asks a real question, classify it as general_question.
- If the user is just greeting or chatting casually, classify it as conversation.

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

Current flow:
{json.dumps(active_flow)}

Last question type asked by the assistant:
{json.dumps(last_question_type)}

User message:
{user_message}

Instructions:
- Respond naturally and conversationally.
- Use the recent conversation as context.
- Do not pretend to have searched listings unless results were actually returned.
- Do not modify search state.
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
- Acknowledge useful information already provided.
- Ask only for the missing required information.
- Do not invent values.
- Do not mention JSON, tools, schemas, validation, or internal logic.
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
- Briefly summarize the most important preferences already captured.
- Do not invent anything.
- Do not mention JSON, tools, schemas, validation, or internal logic.
- Keep it conversational and concise.
- Do not use bullet points.

Return only plain text.
""".strip()