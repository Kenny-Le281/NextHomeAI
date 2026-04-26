from typing import Optional, List, Literal, Any
from pydantic import BaseModel, Field


FlowType = Optional[Literal["search", "booking"]]
QuestionType = Optional[Literal[
    "city",
    "price_max",
    "beds_min",
    "booking_address",
    "booking_name",
    "booking_email",
    "booking_phone",
    "booking_date",
    "booking_time",
    "booking_virtual",
    "booking_confirmation",
    "booking_final_confirmation",
]]


class SessionMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class SessionContext(BaseModel):
    conversation_history: List[SessionMessage] = Field(default_factory=list)
    active_flow: FlowType = None
    last_question_type: QuestionType = None
    latest_listings: List[dict[str, Any]] = Field(default_factory=list)