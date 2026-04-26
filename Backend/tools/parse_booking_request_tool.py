import json
import re

from pydantic import ValidationError

from llm.ollama_client import call_ollama
from llm.prompts import build_booking_parser_prompt
from models.booking_request import BookingParseResult


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


def parse_booking_request_tool(
    user_message: str,
    current_booking: dict,
    current_context: dict,
) -> BookingParseResult:
    prompt = build_booking_parser_prompt(
        user_message=user_message,
        current_booking=current_booking,
        current_context=current_context,
    )
    llm_output = call_ollama(prompt)

    print("=== BOOKING USER MESSAGE ===")
    print(user_message)
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
        return BookingParseResult(
            wants_to_book=False,
            notes=[f"LLM output was not valid JSON: {exception}"]
        )

    try:
        return BookingParseResult.model_validate(parsed_json)
    except ValidationError as exception:
        return BookingParseResult(
            wants_to_book=False,
            notes=[f"Validation failed: {exception}"]
        )