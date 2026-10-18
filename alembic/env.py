import os
from logging.config import fileConfig
from alembic import context
from sqlalchemy import URL, engine_from_config, pool
from finance_manager.db.models import BaseModel


# Alembic configuration.
config = context.config

# Build the database URL from environment variables.
database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["POSTGRES_SUPERUSER_NAME"],
    password=os.environ["POSTGRES_SUPERUSER_PSWRD"],
    host=os.environ.get("DB_HOST", "localhost"),
    port=int(os.environ.get("DB_PORT", "5432")),
    database="personal-finances",
)

# Override sqlalchemy.url from alembic.ini.
# Escape percent signs for ConfigParser interpolation.
config.set_main_option(
    "sqlalchemy.url",
    database_url.render_as_string(hide_password=False).replace("%", "%%"),
)

# Configure Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = BaseModel.metadata


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
