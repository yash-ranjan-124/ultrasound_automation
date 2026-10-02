from alembic import context

from medvision.config import Settings
from medvision.infrastructure.persistence import (
    Base,
    create_database_engine,
    normalize_database_url,
)

config = context.config
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = normalize_database_url(Settings().database_url)
    context.configure(
        url=url.render_as_string(hide_password=True),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_database_engine(Settings().database_url)
    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
