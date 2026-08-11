import psycopg2

from config import (
    DATABASE_CONNECT_TIMEOUT_SECONDS,
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_SSLMODE,
    DATABASE_URL,
    DATABASE_USER,
)


def get_db_connection():
    if DATABASE_URL:
        return psycopg2.connect(
            DATABASE_URL,
            connect_timeout=DATABASE_CONNECT_TIMEOUT_SECONDS,
        )

    missing = [
        name
        for name, value in (
            ("DATABASE_HOST", DATABASE_HOST),
            ("DATABASE_USER", DATABASE_USER),
            ("DATABASE_PASSWORD", DATABASE_PASSWORD),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Database configuration is incomplete. Set DATABASE_URL or provide: "
            + ", ".join(missing)
            + "."
        )

    return psycopg2.connect(
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        sslmode=DATABASE_SSLMODE,
        connect_timeout=DATABASE_CONNECT_TIMEOUT_SECONDS,
    )
