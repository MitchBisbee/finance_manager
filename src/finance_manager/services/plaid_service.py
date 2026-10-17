from uuid import uuid7
from typing import Any, Generator
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from finance_manager.db.models.transaction_models import Transaction, Category
from finance_manager.dtos.transactions import ImportedTransactionDto
from finance_manager.services.interfaces.plaid_factory_interfaces import IPlaidSessionFactory
from finance_manager.utilities.decorators import retry_until_transaction_ready


class PlaidService:
    def __init__(self, session_factory: IPlaidSessionFactory):
        self._client = session_factory.get_client()
        self._access_token = session_factory.get_access_token()

    @retry_until_transaction_ready
    def _get_transactions(self) -> Any:
        return self._client.transactions_sync(
            TransactionsSyncRequest(
                access_token=self._access_token,
                count=500,
            )
        )

    def map_to_imported_transaction_dto(self, response: Any) -> Generator[ImportedTransactionDto, None, None]:
        return (
            ImportedTransactionDto(
                date=response["date"],
                name=response["name"],
                amount=response["amount"],
                transaction_id=response["transaction_id"],
                category=response["category"]
            ) for _ in response["added"]
        )

    def extract_orm_models(
        self, transaction_dtos: Generator[ImportedTransactionDto, None, None]
    ) -> Generator[tuple[Transaction, Category], None, None]:
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
