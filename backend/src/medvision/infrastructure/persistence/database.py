from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL, make_url


def normalize_database_url(database_url: str | None) -> URL:
    if not database_url:
        raise RuntimeError("DATABASE_URL is required for PostgreSQL study persistence.")

    url = make_url(database_url)
    if url.drivername in {"postgres", "postgresql"}:
        return url.set(drivername="postgresql+psycopg")
    if url.drivername == "postgresql+psycopg":
        return url
    raise ValueError("DATABASE_URL must use PostgreSQL with the psycopg driver.")


def create_database_engine(database_url: str | None) -> Engine:
    return create_engine(normalize_database_url(database_url), pool_pre_ping=True)
