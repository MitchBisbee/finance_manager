"""Import Plaid transactions and map them to persistent ORM models.

This module supports initial imports of added transactions. It does not
persist synchronization cursors or process modified and removed transactions.

Repository implementations are responsible for transaction management,
insert ordering, and duplicate prevention.
"""

import json
from collections.abc import Iterable, Iterator
from typing import Any
from uuid import uuid7

from plaid.exceptions import ApiException
from plaid.model.transactions_sync_request import TransactionsSyncRequest

from finance_manager.db.models.transaction_models import Category, Transaction
from finance_manager.db.repositories.transactions_repository import (
    TransactionRepository,
)
from finance_manager.dtos.transactions import ImportedTransactionDto
from finance_manager.services.interfaces.plaid_factory_interfaces import (
    IPlaidSessionFactory,
)
from finance_manager.utilities.decorators import retry_until_transaction_ready


class PlaidService:
    """Import added Plaid transactions through a repository.

    Fetches all transaction pages before mapping and persisting records.
    Pagination mutation errors restart the fetch from the initial cursor,
    subject to a bounded number of attempts.

    The configured client and access token are obtained once during
    initialization and reused for subsequent requests.
    """

    _PAGE_SIZE = 500
    _MAX_PAGINATION_ATTEMPTS = 3
    _PAGINATION_MUTATION_ERROR = (
        "TRANSACTIONS_SYNC_MUTATION_DURING_PAGINATION"
    )

    def __init__(
        self,
        session_factory: IPlaidSessionFactory,
        transaction_repository: TransactionRepository,
    ) -> None:
        """Initialize the service with a Plaid session and repository.

        Args:
            session_factory: Provides the configured Plaid client and access
                token for the linked Item.
            transaction_repository: Persists transaction and category models.
        """
        self._client = session_factory.get_client()
        self._access_token = session_factory.get_access_token()
        self._transaction_repository = transaction_repository

    @retry_until_transaction_ready
    def _get_transactions_from_plaid(
        self,
        cursor: str | None = None,
    ) -> Any:
        """Fetch one page of transaction synchronization results.

        Args:
            cursor: Position from which to fetch changes. If None, the cursor
                is omitted to begin an initial import.

        Returns:
            The Plaid synchronization response, including added transactions,
            pagination state, and the next cursor.

        Raises:
            ApiException: If the Plaid request fails and the exception is not
                handled by the readiness retry decorator.
        """
        request = TransactionsSyncRequest(
            access_token=self._access_token,
            count=self._PAGE_SIZE,
        )

        if cursor is not None:
            request.cursor = cursor

        return self._client.transactions_sync(request)

    def _get_added_transactions(self) -> list[Any]:
        """Collect added transactions across all synchronization pages.

        Each pagination attempt begins without a cursor. If a pagination
        mutation occurs, the partially collected results are discarded and
        the complete pagination sequence is retried.

        Returns:
            Added transaction records from a completed pagination sequence.

        Raises:
            ApiException: If a request fails with a non-pagination error or
                pagination mutations exhaust the allowed attempts.
            RuntimeError: If the pagination attempts finish without returning
                results or propagating an API exception.
        """
        for attempt in range(self._MAX_PAGINATION_ATTEMPTS):
            cursor: str | None = None
            added_transactions: list[Any] = []

            try:
                while True:
                    response = self._get_transactions_from_plaid(cursor)
                    added_transactions.extend(response["added"])

                    if not response["has_more"]:
                        return added_transactions

                    cursor = response["next_cursor"]

            except ApiException as exc:
                is_last_attempt = (
                    attempt == self._MAX_PAGINATION_ATTEMPTS - 1
                )

                if (
                    not self._is_pagination_mutation(exc)
                    or is_last_attempt
                ):
                    raise

        raise RuntimeError(
            "Unable to complete Plaid transaction pagination."
        )

    @classmethod
    def _is_pagination_mutation(cls, error: ApiException) -> bool:
        """Determine whether an API exception indicates a pagination mutation.

        Args:
            error: Plaid API exception whose response body should be examined.

        Returns:
            True if the response body contains the pagination mutation error
            code. False if the body is missing, invalid, or describes another
            error.
        """
        try:
            error_body = json.loads(error.body or "{}")
        except (TypeError, ValueError):
            return False

        return (
            isinstance(error_body, dict)
            and error_body.get("error_code")
            == cls._PAGINATION_MUTATION_ERROR
        )

    def _map_to_imported_transaction_dtos(
        self,
        transactions: Iterable[Any],
    ) -> Iterator[ImportedTransactionDto]:
        """Map Plaid transaction records to application DTOs.

        Args:
            transactions: Plaid transaction records containing the fields
                required by ImportedTransactionDto.

        Yields:
            An imported transaction DTO for each input record.

        Raises:
            KeyError: If an input record is missing a required field.
        """
        for transaction in transactions:
            yield ImportedTransactionDto(
                date=transaction["date"],
                name=transaction["name"],
                amount=transaction["amount"],
                transaction_id=transaction["transaction_id"],
                category=transaction["category"],
            )

    def _extract_orm_models(
        self,
        transaction_dtos: Iterable[ImportedTransactionDto],
    ) -> Iterator[tuple[Transaction, Category]]:
        """Convert transaction DTOs into related ORM model pairs.

        Assigns each transaction a UUID before constructing its category,
        allowing the category to reference the transaction before persistence.

        Args:
            transaction_dtos: Transaction DTOs to convert into ORM models.

        Yields:
            A transaction and its associated category, in that order.
        """
        for dto in transaction_dtos:
            transaction = Transaction(
                id=uuid7(),
                date=dto.date,
                name=dto.name,
                amount=dto.amount,
                bank_transaction_id=dto.transaction_id,
            )

            category = Category(
                transaction_id=transaction.id,
                types=dto.category,
            )

            yield transaction, category

    def persist_transactions(self) -> None:
        """Fetch, map, and persist added Plaid transactions.

        Completes pagination before invoking repository writes. Each
        transaction is passed to the repository before its associated category.

        This method does not explicitly commit or roll back database work.
        Transaction management and duplicate prevention are delegated to the
        repository and its surrounding unit of work.

        Raises:
            ApiException: If fetching transactions fails after applicable
                readiness or pagination retries.
            KeyError: If a transaction is missing a required mapping field.
            RuntimeError: If pagination finishes without a result.
        """
        transactions = self._get_added_transactions()
        transaction_dtos = self._map_to_imported_transaction_dtos(
            transactions
        )

        for transaction, category in self._extract_orm_models(
            transaction_dtos
        ):
            self._transaction_repository.create_transaction(transaction)
            self._transaction_repository.create_category(category)
