"""Manage PostgreSQL connectivity and SQLAlchemy session creation.

The client maintains one engine and session factory per process. Individual
sessions are created for each unit of work and are not shared globally.
"""

from collections.abc import Generator, Mapping
from contextlib import contextmanager
from threading import Lock
from typing import Any, ClassVar
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from finance_manager.connections.interfaces import IClientFactory


class PostgresClient(IClientFactory):
    """Manage a shared PostgreSQL engine and session factory.

    The first construction initializes the singleton. Subsequent construction
    with the same connection string returns the existing instance.

    A different connection string is rejected to avoid silently connecting
    callers to an unexpected database.
    """

    _instance: ClassVar["PostgresClient | None"] = None
    _instance_lock: ClassVar[Lock] = Lock()

    connection_string: str
    _engine: Engine
    _session_factory: sessionmaker[Session]

    def __new__(cls, connection_string: str) -> "PostgresClient":
        """Create or return the singleton client.

        Args:
            connection_string: SQLAlchemy PostgreSQL connection URL.

        Returns:
            The shared PostgreSQL client.

        Raises:
            ValueError: If the connection string is empty or differs from
                the URL used to initialize the existing client.
        """
        if not connection_string.strip():
            raise ValueError("A database connection string is required.")

        with cls._instance_lock:
            if cls._instance is None:
                instance = super().__new__(cls)

                instance.connection_string = connection_string
                instance._engine = create_engine(
                    connection_string,
                    pool_pre_ping=True,
                )
                instance._session_factory = sessionmaker(
                    bind=instance._engine,
                    expire_on_commit=False,
                )

                cls._instance = instance

            elif cls._instance.connection_string != connection_string:
                raise ValueError(
                    "PostgresClient is already initialized with a "
                    "different connection string."
                )

            return cls._instance

    def connect(self) -> None:
        """Verify database connectivity.

        Checks out a connection, executes a lightweight query, and returns
        the connection to the pool. Database errors propagate to the caller.
        """
        with self._engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Provide a session with a managed transaction.

        Commits on successful exit, rolls back if an exception occurs, and
        closes the session in either case.

        Yields:
            A session to use for one unit of work.
        """
        with self._session_factory() as session:
            with session.begin():
                yield session

    def execute_query(
        self,
        query: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute one SQL statement in an independent transaction.

        Uses SQLAlchemy named parameters, such as ``:transaction_id``.
        Statements that return rows are fully materialized before the
        connection is returned to the pool.

        Args:
            query: SQL statement to execute.
            parameters: Optional values for named SQL parameters.

        Returns:
            Result rows as dictionaries, or an empty list if the statement
            does not return rows.

        Note:
            This method does not participate in transactions opened through
            get_session(). Use that session directly when multiple operations
            must succeed or fail together.
        """
        with self._engine.begin() as connection:
            result = connection.execute(
                text(query),
                dict(parameters) if parameters is not None else {},
            )

            if not result.returns_rows:
                return []

            return [dict(row) for row in result.mappings().all()]

    def dispose(self) -> None:
        """Dispose of idle pooled connections.

        Call during application shutdown after active database work has
        finished. The engine can establish new connections if reused.
        """
        self._engine.dispose()


def get_postgres_client(connection_string: str) -> IClientFactory:
    """Return the shared PostgreSQL client.

    Args:
        connection_string: SQLAlchemy PostgreSQL connection URL.

    Returns:
        The singleton PostgreSQL client implementing IClientFactory.
    """
    return PostgresClient(connection_string)
