from llm.ollama_client import call_ollama
from llm.prompts import build_normal_chat_prompt


def normal_chat_tool(
    user_message: str,
    current_filters: dict,
    current_context: dict,
    current_booking: dict,
) -> str:
    prompt = build_normal_chat_prompt(
        user_message=user_message,
        current_filters=current_filters,
        current_context=current_context,
        current_booking=current_booking,
    )
    return call_ollama(prompt).strip()