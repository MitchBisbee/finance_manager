"""Define the transaction repository interface."""

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from uuid import UUID

from finance_manager.db.models.transaction_models import Category, Transaction


class ITransactionRepository(ABC):
    """Define transaction and category persistence operations."""

    @abstractmethod
    def transaction(
        self,
    ) -> AbstractContextManager["ITransactionRepository"]:
        """Provide a transaction context for grouped repository operations.

        Returns:
            A context manager that yields the repository, commits on
            successful exit, and rolls back on an exception.
        """

    @abstractmethod
    def create_transaction(self, transaction: Transaction) -> None:
        """Add and flush a transaction within the active transaction.

        Args:
            transaction: Transaction model to persist.
        """

    @abstractmethod
    def create_category(self, category: Category) -> None:
        """Add and flush a category within the active transaction.

        Args:
            category: Category model to persist.
        """

    @abstractmethod
    def update_transaction(self, transaction: Transaction) -> None:
        """Apply updated state to an existing transaction.

        Args:
            transaction: Model containing the primary key and updated state.

        Raises:
            ValueError: If the transaction does not exist.
        """

    @abstractmethod
    def update_category(self, category: Category) -> None:
        """Apply updated state to an existing category.

        Args:
            category: Model containing the primary key and updated state.

        Raises:
            ValueError: If the category does not exist.
        """

    @abstractmethod
    def get_transaction_by_id(
        self,
        transaction_id: UUID,
    ) -> Transaction | None:
        """Retrieve a transaction by its internal primary key.

        Args:
            transaction_id: Internal UUID, not the Plaid transaction ID.

        Returns:
            The matching transaction, or None if no record exists.
        """

    @abstractmethod
    def get_category_by_transaction_id(
        self,
        transaction_id: UUID,
    ) -> Category | None:
        """Retrieve the category associated with a transaction.

        Args:
            transaction_id: Internal UUID of the associated transaction.

        Returns:
            The matching category, or None if no record exists.
        """

    @abstractmethod
    def delete_transaction(self, transaction_id: UUID) -> None:
        """Delete a transaction and its associated categories.

        Args:
            transaction_id: Internal UUID of the transaction to delete.

        Raises:
            ValueError: If the transaction does not exist.
        """

    @abstractmethod
    def delete_category(self, transaction_id: UUID) -> None:
        """Delete the category associated with a transaction.

        Args:
            transaction_id: Internal UUID of the associated transaction.

        Raises:
            ValueError: If no category exists for the transaction.
        """
