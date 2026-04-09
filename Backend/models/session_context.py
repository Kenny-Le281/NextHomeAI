from typing import Optional, List, Literal
from pydantic import BaseModel, Field


FlowType = Optional[Literal["search"]]
QuestionType = Optional[Literal[
    "city",
    "price_max",
    "beds_min",
]]


class SessionMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class SessionContext(BaseModel):
    conversation_history: List[SessionMessage] = Field(default_factory=list)
    active_flow: FlowType = None
    last_question_type: QuestionType = None