import json
import re

from pydantic import ValidationError

from llm.openai_client import call_llm
from llm.prompts import build_intent_classifier_prompt
from models.intent import IntentResult


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


def classify_intent_tool(
    user_message: str,
    current_filters: dict,
    current_context: dict,
    current_booking: dict,
) -> IntentResult:
    prompt = build_intent_classifier_prompt(
        user_message=user_message,
        current_filters=current_filters,
        current_context=current_context,
        current_booking=current_booking,
    )
    llm_output = call_llm(prompt)

    print("=== RAW LLM OUTPUT ===")
    print(llm_output)
    print()

    clean_output = extract_json_text(llm_output)

    print("=== CLEANED LLM OUTPUT ===")
    print(clean_output)
    print()

    try:
        parsed_json = json.loads(clean_output)
    except json.JSONDecodeError:
        return IntentResult(
            intent="conversation",
            reason="Failed to parse classifier output; defaulted to conversation."
        )

    try:
        return IntentResult.model_validate(parsed_json)
    except ValidationError:
        return IntentResult(
            intent="conversation",
            reason="Classifier output failed validation; defaulted to conversation."
        )
