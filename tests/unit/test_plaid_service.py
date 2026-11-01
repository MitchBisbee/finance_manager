"""Unit tests for the plaid_service module."""
import json
from datetime import date
from unittest.mock import create_autospec, patch

import pytest
from plaid.api.plaid_api import PlaidApi
from plaid.exceptions import ApiException
from plaid.model.transactions_update_status import TransactionsUpdateStatus

from db.models import Category, Transaction
from db.repositories.interfaces import ITransactionRepository
from airflow_etl.services import get_plaid_service
from airflow_etl.services.interfaces.plaid_factory_interfaces import (
    IPlaidSessionFactory,
)


@pytest.fixture
def plaid_client():
    return create_autospec(PlaidApi, instance=True)


@pytest.fixture
def session_factory(plaid_client):
    factory = create_autospec(IPlaidSessionFactory, instance=True)
    factory.get_client.return_value = plaid_client
    factory.get_access_token.return_value = "access-sandbox-token"
    return factory


@pytest.fixture
def transaction_repository():
    return create_autospec(ITransactionRepository, instance=True)


@pytest.fixture
def plaid_service(session_factory, transaction_repository):
    return get_plaid_service(
        session_factory=session_factory,
        transaction_repository=transaction_repository,
    )


@pytest.fixture
def no_sleep():
    with patch(
        "airflow_etl.utilities.decorators.sleep", autospec=True
    ) as sleep:
        yield sleep


@pytest.fixture
def make_plaid_transaction():
    """Return a builder for Plaid transaction payloads."""
    def _make(transaction_id="txn-1", **overrides):
        payload = {
            "date": date(2025, 7, 1),
            "name": f"Vendor {transaction_id}",
            "amount": 12.5,
            "transaction_id": transaction_id,
            "category": ["Shops"],
        }
        payload.update(overrides)
        return payload
    return _make


@pytest.fixture
def make_sync_page():
    """Return a builder for /transactions/sync response pages."""
    def _make(added=(), has_more=False, next_cursor="",
              status="HISTORICAL_UPDATE_COMPLETE"):
        return {
            "added": list(added),
            "has_more": has_more,
            "next_cursor": next_cursor,
            "transactions_update_status": TransactionsUpdateStatus(status),
        }
    return _make


@pytest.fixture
def make_api_exception():
    """Return a builder for Plaid API exceptions with a JSON error body."""
    def _make(error_code="INTERNAL_SERVER_ERROR", status=400):
        error = ApiException(status=status)
        error.body = json.dumps({"error_code": error_code})
        return error
    return _make


class TestHappyPaths:
    @pytest.mark.parametrize(
        "page_count",
        [1, 2, 3],
        ids=["single-page", "two-pages", "three-pages"],
    )
    def test_extract_fetches_every_page(
        self, plaid_service, plaid_client, make_plaid_transaction,
        make_sync_page, page_count,
    ):
        plaid_client.transactions_sync.side_effect = [
            make_sync_page(
                added=[make_plaid_transaction(f"txn-{page}")],
                has_more=page < page_count - 1,
                next_cursor=f"cursor-{page}",
            )
            for page in range(page_count)
        ]

        extracted = plaid_service.extract()

        assert plaid_client.transactions_sync.call_count == page_count
        assert len(extracted) == page_count

    def test_extract_passes_next_cursor(
        self, plaid_service, plaid_client, make_plaid_transaction,
        make_sync_page,
    ):
        plaid_client.transactions_sync.side_effect = [
            make_sync_page(added=[make_plaid_transaction("a")],
                           has_more=True, next_cursor="cursor-1"),
            make_sync_page(added=[make_plaid_transaction("b")]),
        ]

        plaid_service.extract()

        requests = [call.args[0]
                    for call in plaid_client.transactions_sync.call_args_list]
        assert "cursor" not in requests[0]
        assert requests[1].cursor == "cursor-1"

    def test_extract_does_not_touch_repository(
        self, plaid_service, plaid_client, transaction_repository,
        make_plaid_transaction, make_sync_page,
    ):
        plaid_client.transactions_sync.return_value = make_sync_page(
            added=[make_plaid_transaction()])

        plaid_service.extract()

        assert transaction_repository.method_calls == []

    def test_transform_maps_plaid_fields(
        self, plaid_service, make_plaid_transaction,
    ):
        payload = make_plaid_transaction("txn-42", amount=99.99,
                                         category=["Food", "Coffee"])

        [(transaction, category)] = plaid_service.transform([payload])

        assert isinstance(transaction, Transaction)
        assert (transaction.bank_transaction_id, transaction.name,
                transaction.amount, transaction.date) == (
            "txn-42", payload["name"], 99.99, payload["date"])
        assert isinstance(category, Category)
        assert category.transaction_id == transaction.id
        assert category.types == ["Food", "Coffee"]

    def test_transform_does_not_touch_plaid_or_repository(
        self, plaid_service, plaid_client, transaction_repository,
        make_plaid_transaction,
    ):
        plaid_service.transform([make_plaid_transaction()])

        plaid_client.transactions_sync.assert_not_called()
        assert transaction_repository.method_calls == []

    def test_transform_with_no_transactions_returns_empty_list(
        self, plaid_service,
    ):
        records = plaid_service.transform([])

        assert records == []

    def test_load_saves_transaction_before_category(
        self, plaid_service, transaction_repository, make_plaid_transaction,
    ):
        records = plaid_service.transform(
            [make_plaid_transaction("a"), make_plaid_transaction("b")])

        plaid_service.load(records)

        assert [call[0] for call in transaction_repository.method_calls] == [
            "create_transaction", "create_category",
            "create_transaction", "create_category",
        ]

    def test_load_passes_each_model_to_repository(
        self, plaid_service, transaction_repository, make_plaid_transaction,
    ):
        records = plaid_service.transform([make_plaid_transaction()])
        [(transaction, category)] = records

        plaid_service.load(records)

        transaction_repository.create_transaction.assert_called_once_with(
            transaction)
        transaction_repository.create_category.assert_called_once_with(
            category)

    def test_load_with_no_records_saves_nothing(
        self, plaid_service, transaction_repository,
    ):
        plaid_service.load([])

        assert transaction_repository.method_calls == []


class TestUnhappyPaths:
    def test_pagination_mutation_restarts_from_initial_cursor(
        self, plaid_service, plaid_client, make_plaid_transaction,
        make_sync_page, make_api_exception,
    ):
        plaid_client.transactions_sync.side_effect = [
            make_sync_page(added=[make_plaid_transaction("stale")],
                           has_more=True, next_cursor="cursor-1"),
            make_api_exception("TRANSACTIONS_SYNC_MUTATION_DURING_PAGINATION"),
            make_sync_page(added=[make_plaid_transaction("fresh")]),
        ]

        extracted = plaid_service.extract()

        restart_request = plaid_client.transactions_sync.call_args_list[2].args[0]
        assert "cursor" not in restart_request
        assert [item["transaction_id"] for item in extracted] == ["fresh"]

    def test_pagination_mutation_raises_after_max_attempts(
        self, plaid_service, plaid_client, make_api_exception,
    ):
        plaid_client.transactions_sync.side_effect = make_api_exception(
            "TRANSACTIONS_SYNC_MUTATION_DURING_PAGINATION")

        with pytest.raises(ApiException):
            plaid_service.extract()

        assert plaid_client.transactions_sync.call_count == 3

    @pytest.mark.parametrize(
        "body",
        [json.dumps({"error_code": "ITEM_LOGIN_REQUIRED"}), "not json", None],
        ids=["other-error-code", "invalid-json-body", "missing-body"],
    )
    def test_non_mutation_api_error_raises_without_retry(
        self, plaid_service, plaid_client, make_api_exception, body,
    ):
        error = make_api_exception()
        error.body = body
        plaid_client.transactions_sync.side_effect = error

        with pytest.raises(ApiException):
            plaid_service.extract()

        assert plaid_client.transactions_sync.call_count == 1

    def test_not_ready_status_retries_until_ready(
        self, plaid_service, plaid_client, make_plaid_transaction,
        make_sync_page, no_sleep,
    ):
        plaid_client.transactions_sync.side_effect = [
            make_sync_page(status="NOT_READY"),
            make_sync_page(added=[make_plaid_transaction()]),
        ]

        extracted = plaid_service.extract()

        assert plaid_client.transactions_sync.call_count == 2
        no_sleep.assert_called_once_with(3)
        assert len(extracted) == 1

    def test_not_ready_status_times_out(
        self, plaid_service, plaid_client, make_sync_page, no_sleep,
    ):
        plaid_client.transactions_sync.return_value = make_sync_page(
            status="NOT_READY")

        with pytest.raises(TimeoutError, match="NOT_READY after 20 attempts"):
            plaid_service.extract()

        assert no_sleep.call_count == 19

    @pytest.mark.parametrize(
        "missing_field",
        ["date", "name", "amount", "transaction_id", "category"],
        ids=["no-date", "no-name", "no-amount", "no-transaction-id",
             "no-category"],
    )
    def test_transform_missing_plaid_field_raises_key_error(
        self, plaid_service, make_plaid_transaction, missing_field,
    ):
        payload = make_plaid_transaction()
        del payload[missing_field]

        with pytest.raises(KeyError, match=missing_field):
            plaid_service.transform([payload])
