"""Manage transaction and category persistence through a PostgreSQL client."""
from collections.abc import Generator
from contextlib import contextmanager
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from finance_manager.db.models.transaction_models import Category, Transaction
from finance_manager.db.connections import PostgresClient
from finance_manager.repositories.interfaces import ITransactionRepository
from finance_manager.db.repositories.interfaces import IClientFactory


class TransactionRepository(ITransactionRepository):
    """Manage transaction and category records within an explicit transaction.

    A repository instance supports one active transaction at a time and
    must not be shared across concurrent units of work.
    """

    def __init__(self, db_client: IClientFactory) -> None:
        """Initialize the repository.

        Args:
            db_client: Client that provides managed database sessions.
        """
        self._postgres_client = db_client
        self._session: Session | None = None

    @contextmanager
    def transaction(self) -> Generator["TransactionRepository", None, None]:
        """Open a shared session for a group of repository operations.

        The PostgreSQL client's session context commits on successful exit,
        rolls back on an exception, and closes the session.

        Yields:
            This repository with an active database session.

        Raises:
            RuntimeError: If this repository already has an active transaction.
        """
        if self._session is not None:
            raise RuntimeError(
                "This repository already has an active transaction."
            )

        with self._postgres_client.get_session() as session:
            self._session = session

            try:
                yield self
            finally:
                self._session = None

    def _get_session(self) -> Session:
        """Return the session for the active transaction.

        Returns:
            The active database session.

        Raises:
            RuntimeError: If no repository transaction is active.
        """
        if self._session is None:
            raise RuntimeError(
                "Repository operations require an active transaction. "
                "Use 'with repository.transaction():'."
            )

        return self._session

    def create_transaction(self, transaction: Transaction) -> None:
        """Add and flush a new transaction without committing.

        Args:
            transaction: Transaction model to persist.
        """
        session = self._get_session()
        session.add(transaction)
        session.flush()

    def create_category(self, category: Category) -> None:
        """Add and flush a new category without committing.

        Args:
            category: Category model to persist. Its transaction must already
                exist or have been flushed in the active session.
        """
        session = self._get_session()
        session.add(category)
        session.flush()

    def update_transaction(self, transaction: Transaction) -> None:
        """Apply a transaction model's state to an existing record.

        Args:
            transaction: Model containing the primary key and updated state.

        Raises:
            ValueError: If the transaction does not exist.

        Note:
            This is a full-state merge, not a partial-field update. The
            supplied model is not necessarily the session-managed instance.
        """
        session = self._get_session()
        existing = session.get(Transaction, transaction.id)

        if existing is None:
            raise ValueError(
                f"Transaction with ID {transaction.id} does not exist."
            )

        session.merge(transaction)
        session.flush()

    def update_category(self, category: Category) -> None:
        """Apply a category model's state to an existing record.

        Args:
            category: Model containing the primary key and updated state.

        Raises:
            ValueError: If the category does not exist.

        Note:
            This is a full-state merge, not a partial-field update. The
            supplied model is not necessarily the session-managed instance.
        """
        session = self._get_session()
        existing = session.get(Category, category.id)

        if existing is None:
            raise ValueError(
                f"Category with ID {category.id} does not exist."
            )

        session.merge(category)
        session.flush()

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
        return self._get_session().get(Transaction, transaction_id)

    def get_category_by_transaction_id(
        self,
        transaction_id: UUID,
    ) -> Category | None:
        """Retrieve the category associated with a transaction.

        Args:
            transaction_id: Internal UUID of the associated transaction.

        Returns:
            The matching category, or None if no record exists.

        Raises:
            sqlalchemy.exc.MultipleResultsFound: If more than one category
                exists for the transaction.
        """
        statement = select(Category).where(
            Category.transaction_id == transaction_id
        )

        return (
            self._get_session()
            .execute(statement)
            .scalar_one_or_none()
        )

    def delete_transaction(self, transaction_id: UUID) -> None:
        """Delete a transaction and its associated categories.

        Category deletions are flushed before deleting the transaction.

        Args:
            transaction_id: Internal UUID of the transaction to delete.

        Raises:
            ValueError: If the transaction does not exist.

        Note:
            Other referencing tables may require additional deletion handling
            or configured database cascades.
        """
        session = self._get_session()
        transaction = session.get(Transaction, transaction_id)

        if transaction is None:
            raise ValueError(
                f"Transaction with ID {transaction_id} does not exist."
            )

        statement = select(Category).where(
            Category.transaction_id == transaction_id
        )
        categories = session.scalars(statement).all()

        for category in categories:
            session.delete(category)

        session.flush()
        session.delete(transaction)
        session.flush()

    def delete_category(self, transaction_id: UUID) -> None:
        """Delete the category associated with a transaction.

        Args:
            transaction_id: Internal UUID of the associated transaction.

        Raises:
            ValueError: If no category exists for the transaction.
            sqlalchemy.exc.MultipleResultsFound: If more than one category
                exists for the transaction.
        """
        session = self._get_session()
        category = self.get_category_by_transaction_id(transaction_id)

        if category is None:
            raise ValueError(
                "Category for transaction "
                f"{transaction_id} does not exist."
            )

        session.delete(category)
        session.flush()


def get_transaction_repository(db_client: IClientFactory) -> ITransactionRepository:
    """Return a new instance of the transaction repository.

    Returns:
        A new TransactionRepository instance.
    """
    return TransactionRepository(db_client)
