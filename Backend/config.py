import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _get_int(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))
    if value < 0:
        raise RuntimeError(f"{name} must be zero or greater; received {value}.")
    return value


def _get_float(name: str, default: float) -> float:
    value = float(os.getenv(name, str(default)))
    if value <= 0:
        raise RuntimeError(f"{name} must be greater than zero; received {value}.")
    return value


def _get_csv(name: str, default: str = "") -> list[str]:
    return [
        item.strip().rstrip("/")
        for item in os.getenv(name, default).split(",")
        if item.strip()
    ]


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip().upper()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
OPENAI_TIMEOUT_SECONDS = _get_float("OPENAI_TIMEOUT_SECONDS", 180)

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = _get_int("DATABASE_PORT", 5432)
DATABASE_NAME = os.getenv("DATABASE_NAME", "postgres")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD") or os.getenv("SUPABASE_DB_PASSWORD")
DATABASE_SSLMODE = os.getenv("DATABASE_SSLMODE", "require")
DATABASE_CONNECT_TIMEOUT_SECONDS = _get_int("DATABASE_CONNECT_TIMEOUT_SECONDS", 10)

ALLOWED_ORIGINS = _get_csv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
RATE_LIMIT_REQUESTS = _get_int("RATE_LIMIT_REQUESTS", 60)
RATE_LIMIT_WINDOW_SECONDS = _get_int("RATE_LIMIT_WINDOW_SECONDS", 60)

REDFIN_KEY = os.getenv("REDFIN_KEY")
