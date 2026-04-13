from typing import Literal
from pydantic import BaseModel


IntentType = Literal[
    "provide_search_info",
    "refine_search",
    "general_question",
    "conversation",
    "confirm_search",
    "end_chat",
]


class IntentResult(BaseModel):
    intent: IntentType
    reason: str
