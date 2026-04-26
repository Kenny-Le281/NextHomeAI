from typing import Literal
from pydantic import BaseModel


IntentType = Literal[
    "provide_search_info",
    "refine_search",
    "general_question",
    "conversation",
    "confirm_search",
    "start_booking",
    "provide_booking_info",
    "confirm_booking",
    "end_chat",
]


class IntentResult(BaseModel):
    intent: IntentType
    reason: str
