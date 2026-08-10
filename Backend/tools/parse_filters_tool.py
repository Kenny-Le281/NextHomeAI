import json
import re

from pydantic import ValidationError

from llm.openai_client import call_llm
from llm.prompts import build_filter_parser_prompt
from models.housing_filters import HousingFilters


def extract_json_text(text: str) -> str:
    text = text.strip()
    text = text.replace("```json", "```")
    text = text.replace("```JSON", "```")
    text = text.replace("```", "")
    text = re.sub(r"//.*", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end < start:
        return text.strip()

    return text[start:end + 1].strip()


def parse_filters_tool(
    user_query: str,
    current_filters: dict,
    current_context: dict,
) -> HousingFilters:
    prompt = build_filter_parser_prompt(
        user_query=user_query,
        current_filters=current_filters,
        current_context=current_context,
    )
    llm_output = call_llm(prompt)

    print("=== USER QUERY ===")
    print(user_query)
    print()

    print("=== RAW LLM OUTPUT ===")
    print(llm_output)
    print()

    clean_output = extract_json_text(llm_output)

    print("=== CLEANED LLM OUTPUT ===")
    print(clean_output)
    print()

    try:
        parsed_json = json.loads(clean_output)
    except json.JSONDecodeError as exception:
        return HousingFilters(notes=[f"LLM output was not valid JSON: {exception}"])

    try:
        return HousingFilters.model_validate(parsed_json)
    except ValidationError as exception:
        return HousingFilters(notes=[f"Validation failed: {exception}"])
