"""Alembic environment configuration."""

import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import get_settings
from app.models.base import Base  # Import base model

# Import all models so they're registered with SQLAlchemy
from app.models.user import User  # noqa: F401
from app.models.developer import Developer  # noqa: F401
from app.models.property import Property  # noqa: F401
from app.models.property_image import PropertyImage  # noqa: F401
from app.models.property_document import PropertyDocument  # noqa: F401
from app.models.favorite import Favorite  # noqa: F401
from app.models.lead import Lead  # noqa: F401
from app.models.review import Review  # noqa: F401
from app.models.view_history import ViewHistory  # noqa: F401
from app.models.search_history import SearchHistory  # noqa: F401
from app.models.complex import Complex  # noqa: F401
from app.models.complex_image import ComplexImage  # noqa: F401
from app.models.booking import Booking  # noqa: F401
from app.models.promo_code import PromoCode  # noqa: F401
from app.models.dynamic_pricing import DynamicPricing  # noqa: F401
from app.models.mongodb import *  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get settings
settings = get_settings()

# Set the database URL from settings
config.set_main_option("sqlalchemy.url", settings.get_database_url())

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with provided connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = create_async_engine(
        settings.get_database_url(),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
