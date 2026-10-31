"""Define the database client factory interface."""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from contextlib import AbstractContextManager
from typing import Any

from sqlalchemy.orm import Session


class IClientFactory(ABC):
    """Define database connectivity, session creation, and query operations."""

    @abstractmethod
    def connect(self) -> None:
        """Verify database connectivity.

        Database connection errors propagate to the caller.
        """

    @abstractmethod
    def get_session(self) -> AbstractContextManager[Session]:
        """Provide a session with a managed transaction.

        Returns:
            A context manager that yields a session, commits on successful
            exit, rolls back on an exception, and closes the session.
        """

    @abstractmethod
    def execute_query(
        self,
        query: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute one SQL statement in an independent transaction.

        Args:
            query: SQL statement using SQLAlchemy named parameters.
            parameters: Optional values for named SQL parameters.

        Returns:
            Result rows as dictionaries, or an empty list if the statement
            does not return rows.

        Note:
            This operation does not participate in transactions opened
            through get_session().
        """

    @abstractmethod
    def dispose(self) -> None:
        """Release idle pooled database connections.

        Call after active database work has finished.
        """
