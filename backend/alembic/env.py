import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

config = context.config
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except Exception:
        pass

# Import all models so Alembic can detect them
from app.database import Base
import app.models  # noqa: F401

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    import os
    from dotenv import load_dotenv
    from sqlalchemy.ext.asyncio import create_async_engine
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    db_url = os.environ["DATABASE_URL"]

    # Supabase uses PgBouncer in transaction mode which doesn't support prepared
    # statements — disable the cache via the asyncpg URL query param.
    separator = "&" if "?" in db_url else "?"
    db_url = f"{db_url}{separator}prepared_statement_cache_size=0"

    connectable = create_async_engine(db_url, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
