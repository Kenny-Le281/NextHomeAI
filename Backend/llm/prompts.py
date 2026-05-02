import json


def build_filter_parser_prompt(user_query: str) -> str:
    schema_example = {
        "location": {
            "city": "",
            "region_id": None,
            "radius_km": None,
            "neighborhoods": []
        },
        "price": {
            "min": None,
            "max": None,
            "currency": "CAD"
        },
        "beds_min": None,
        "beds_max": None,
        "baths_min": None,
        "baths_max": None,
        "property_types": [],
        "must_have": [],
        "nice_to_have": [],
        "move_in": None,
        "min_sqft": None,
        "min_lot_size": None,
        "notes": []
    }

    return f"""
You are a housing search filter parser.

Convert the user's housing request into VALID JSON only.

Rules:
- Return valid JSON only.
- Do not include markdown.
- Do not include triple backticks.
- Do not include comments.
- Do not include explanations.
- Do not include API parameters or numeric API codes.
- Use semantic values only.
- Example: use "house", not 1.
- Do not invent neighborhoods or areas not explicitly stated by the user.
- If the user only mentions a city (e.g. "Ottawa"), leave neighborhoods as an empty list.
- Use exactly this schema:
{json.dumps(schema_example, indent=2)}

Important rules:
- Leave unknown values as null or [].
- Default currency to CAD unless the user clearly says otherwise.
- "budget", "up to", "max", "under", "no more than" → set as price max.
- "at least", "min", "starting from", "above" → set as price min.
- Only put something in "must_have" if the user clearly says it is required, mandatory, must-have, needs, or required.
- If the user says "would be nice", "preferred", "ideally", or similar, put it in "nice_to_have".
- If the user gives a range like "1 or 2 bathrooms", use baths_min=1 and baths_max=2.

Normalization rules:
- "laundry", "washer/dryer", "in-unit laundry" -> "in_unit_laundry"
- "cat friendly", "cats allowed" -> "cat_friendly"
- "dog friendly", "dogs allowed" -> "dog_friendly"
- "parking" -> "parking"
- "gym" -> "gym"
- "air conditioning" -> "ac"
- "pool" -> "pool"
- "garage" -> "garage"
- If the user says something like "Kanata, Ottawa", set city="Ottawa" and neighborhoods=["Kanata"].
- Convert move-in dates to YYYY-MM-DD when possible.
- Put minimum square footage into "min_sqft".
- Put minimum lot size into "min_lot_size".
- If something important is unclear, add a short note in "notes".

User query:
{user_query}
""".strip()


def build_intent_classifier_prompt(user_message: str, current_filters: dict) -> str:
    schema_example = {
        "intent": "provide_search_info",
        "reason": "The user is giving property requirements."
    }

    return f"""
You are an intent classifier for a real estate chatbot.

Classify the user's latest message into exactly one of these intents:

- provide_search_info
  Use this when the user is giving initial property requirements.

- refine_search
  Use this when the user is modifying, adding, or removing property requirements already discussed.

- general_question
  Use this when the user is asking a question that should be answered conversationally rather than parsed as search filters.

- conversation
  Use this for greetings, casual chat, or non-search conversational turns.

- confirm_search
  Use this when the user is confirming the collected search info or asking to proceed.

- end_chat
  Use this when the user wants to exit or stop the conversation.

Current filters:
{json.dumps(current_filters, indent=2)}

User message:
{user_message}

Rules:
- Return valid JSON only.
- Do not include markdown.
- Do not include triple backticks.
- Do not include comments.
- Use exactly this schema:
{json.dumps(schema_example, indent=2)}
- "general_question" should be used for questions like:
  "What does townhouse mean?"
  "Why do you need my budget?"
  "Is Kanata expensive?"
- "conversation" should be used for casual messages like:
  "Hi"
  "Thanks"
  "How are you?"
- "provide_search_info" and "refine_search" should only be used when the user is clearly giving or changing property requirements.
""".strip()


def build_normal_chat_prompt(user_message: str, current_filters: dict) -> str:
    return f"""
You are a helpful real estate chatbot.

The user is not currently giving structured search filters. Respond naturally and helpfully.

Current known filters:
{json.dumps(current_filters, indent=2)}

User message:
{user_message}

Instructions:
- Answer naturally and conversationally.
- If relevant, you may refer to the current filters.
- Do not pretend to have searched listings.
- Do not invent facts about specific listings.
- Do not modify the user's filters.
- Keep the reply concise but useful.
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


def build_listings_summary_prompt(current_filters: dict, listings: list[dict]) -> str:
    return f"""
You are a helpful real estate search assistant.

The user searched with these preferences:
{json.dumps(current_filters, indent=2)}

Here are the matching listings from the database:
{json.dumps(listings, indent=2)}

Instructions:
- Summarize the results naturally and conversationally.
- Mention how many results were found.
- Highlight a few standout properties (best price, most bedrooms, etc.).
- Include the address and price for properties you mention.
- If no results were found, let the user know and suggest broadening their search.
- Do not mention JSON, SQL, databases, or internal logic.
- Keep it concise and helpful.
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
