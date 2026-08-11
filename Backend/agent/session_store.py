import threading
from copy import deepcopy

from models.booking_request import BookingRequest
from models.housing_filters import HousingFilters
from models.session_context import SessionContext, SessionMessage


_sessions: dict[str, dict] = {}
_sessions_lock = threading.Lock()


def create_default_session() -> dict:
    opening_message = "Hi! Tell me what kind of property you're looking for."
    return {
        "filters": HousingFilters(),
        "booking": BookingRequest(),
        "context": SessionContext(
            conversation_history=[SessionMessage(role="assistant", content=opening_message)]
        ),
    }


def get_session(session_id: str) -> dict:
    with _sessions_lock:
        if session_id not in _sessions:
            _sessions[session_id] = create_default_session()
        return deepcopy(_sessions[session_id])


def update_session(
    session_id: str,
    filters: HousingFilters,
    context: SessionContext,
    booking: BookingRequest,
) -> None:
    with _sessions_lock:
        _sessions[session_id] = deepcopy(
            {"filters": filters, "context": context, "booking": booking}
        )


def reset_session(session_id: str) -> None:
    with _sessions_lock:
        _sessions[session_id] = create_default_session()
