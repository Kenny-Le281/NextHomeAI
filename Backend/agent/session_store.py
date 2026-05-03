from models.housing_filters import HousingFilters
from models.session_context import SessionContext


session_store = {
    "filters": HousingFilters(),
    "context": SessionContext(),
}


def get_filters() -> HousingFilters:
    return session_store["filters"]


def set_filters(filters: HousingFilters) -> None:
    session_store["filters"] = filters


def get_context() -> SessionContext:
    return session_store["context"]


def set_context(context: SessionContext) -> None:
    session_store["context"] = context


def reset_session() -> None:
    session_store["filters"] = HousingFilters()
    session_store["context"] = SessionContext()