from functools import lru_cache

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TIMEOUT_SECONDS


@lru_cache(maxsize=1)
def _get_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Add it to the project-root .env file and "
            "restart the backend."
        )

    return OpenAI(
        api_key=OPENAI_API_KEY,
        timeout=OPENAI_TIMEOUT_SECONDS,
    )


def call_llm(prompt: str) -> str:
    try:
        response = _get_client().responses.create(
            model=OPENAI_MODEL,
            input=prompt,
        )
    except APITimeoutError as exception:
        raise RuntimeError(
            f"OpenAI request timed out after {OPENAI_TIMEOUT_SECONDS} seconds: {exception}"
        ) from exception
    except APIConnectionError as exception:
        raise RuntimeError(f"Could not connect to the OpenAI API: {exception}") from exception
    except APIStatusError as exception:
        raise RuntimeError(
            f"OpenAI API request failed with status {exception.status_code}: {exception}"
        ) from exception

    output = response.output_text
    if not output:
        raise RuntimeError("The OpenAI API returned an empty response.")

    return output
