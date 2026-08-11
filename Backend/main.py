import logging
import threading
import time
import uuid
from collections import defaultdict, deque
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from agent.agent_orchestrator import run_agent
from agent.session_store import get_session, reset_session, update_session
from config import (
    ALLOWED_ORIGINS,
    LOG_LEVEL,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW_SECONDS,
)
from models.session_context import SessionMessage


logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("nexthomeai.api")


app = FastAPI(title="NextHomeAI Backend")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10_000)
    session_id: str = Field(min_length=1, max_length=128)


class ResetRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)


_rate_limit_buckets: dict[str, deque[float]] = defaultdict(deque)
_rate_limit_lock = threading.Lock()


def _rate_limit_response(request: Request) -> JSONResponse | None:
    if (
        RATE_LIMIT_REQUESTS == 0
        or request.method == "OPTIONS"
        or request.url.path == "/health"
    ):
        return None

    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS

    with _rate_limit_lock:
        bucket = _rate_limit_buckets[client_ip]
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT_REQUESTS:
            retry_after = max(1, int(RATE_LIMIT_WINDOW_SECONDS - (now - bucket[0])) + 1)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        f"Rate limit exceeded for client {client_ip}: maximum "
                        f"{RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW_SECONDS} seconds. "
                        f"Retry in {retry_after} seconds."
                    )
                },
                headers={"Retry-After": str(retry_after)},
            )
        bucket.append(now)

    return None


@app.middleware("http")
async def request_logging_and_rate_limit(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    started_at = time.perf_counter()
    rate_limit_response = _rate_limit_response(request)

    if rate_limit_response is not None:
        response = rate_limit_response
    else:
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(
                "unhandled_request_error request_id=%s method=%s path=%s",
                request_id,
                request.method,
                request.url.path,
                exc_info=(type(exc), exc, exc.__traceback__),
            )
            response = JSONResponse(
                status_code=500,
                content={"detail": f"{type(exc).__name__}: {exc}"},
            )

    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_completed request_id=%s method=%s path=%s status=%s duration_ms=%.2f client=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - started_at) * 1000,
        request.client.host if request.client else "unknown",
    )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Request-ID"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty or whitespace.")

    try:
        session = get_session(request.session_id)
        current_filters = session["filters"]
        current_context = session["context"]
        current_booking = session["booking"]

        current_context.conversation_history.append(
            SessionMessage(role="user", content=message)
        )
        result = run_agent(
            user_input=message,
            current_filters=current_filters,
            current_context=current_context,
            current_booking=current_booking,
        )

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
    except Exception as exc:
        logger.exception("chat_request_failed session_id=%s", request.session_id)
        # Detailed exception text is intentionally retained at the user's request.
        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc}",
        ) from exc

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
    try:
        reset_session(request.session_id)
    except Exception as exc:
        logger.exception("session_reset_failed session_id=%s", request.session_id)
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}") from exc
    return {"status": "reset"}
