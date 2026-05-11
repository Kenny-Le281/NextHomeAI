from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.agent_orchestrator import run_agent
from models.session_context import SessionMessage
from agent.session_store import get_session, update_session, reset_session


app = FastAPI(title="NextHomeAI Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ResetRequest(BaseModel):
    session_id: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    session = get_session(request.session_id)

    current_filters = session["filters"]
    current_context = session["context"]
    current_booking = session["booking"]

    current_context.conversation_history.append(
        SessionMessage(role="user", content=message)
    )

    try:
        result = run_agent(
            user_input=message,
            current_filters=current_filters,
            current_context=current_context,
            current_booking=current_booking,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    updated_filters = result["filters"]
    updated_context = result["context"]
    updated_booking = result["booking"]

    assistant_reply = result["reply"]

    updated_context.conversation_history.append(
        SessionMessage(role="assistant", content=assistant_reply)
    )

    update_session(
        session_id=request.session_id,
        filters=updated_filters,
        context=updated_context,
        booking=updated_booking,
    )

    return {
        "reply": assistant_reply,
        "filters": updated_filters.model_dump(mode="json"),
        "context": updated_context.model_dump(mode="json"),
        "booking": updated_booking.model_dump(mode="json"),
        "done": result.get("done", False),
        "api_params": result.get("api_params"),
        "listings": result.get("listings"),
        "intent": result.get("intent"),
    }


@app.post("/reset")
def reset(request: ResetRequest):
    reset_session(request.session_id)
    return {"status": "reset"}