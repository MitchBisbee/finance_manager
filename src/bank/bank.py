import os
from typing import Any
from dataclasses import dataclass
from functools import wraps
from time import sleep
from plaid import ApiClient, Configuration, Environment
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.api.plaid_api import PlaidApi
from plaid.model.transactions_sync_request import TransactionsSyncRequest
configuration = Configuration(
    host=Environment.Sandbox,
    api_key={
        "clientId": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
    },
)

client = PlaidApi(ApiClient(configuration))

sandbox_response = client.sandbox_public_token_create(
    SandboxPublicTokenCreateRequest(
        institution_id="ins_109508",
        initial_products=[Products("transactions")],
    )
)

public_token = sandbox_response["public_token"]
sandbox_token_exchange_repsonse = client.item_public_token_exchange(
    ItemPublicTokenExchangeRequest(
        public_token=public_token
    )
)


@dataclass
class Transaction:
    date: str
    name: str
    amount: str
    id: str


@dataclass
class Transactions:
    transactions: list[Transaction]


def retry_until_transaction_ready(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        max_attempts = kwargs.pop("max_attempts", 20)
        delay = kwargs.pop("delay", 3)

        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")
        if delay < 0:
            raise ValueError("delay must be non-negative.")

        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                print(attempt)
                sleep(delay)
            response = func(*args, **kwargs)
            if response["transactions_update_status"].value != "NOT_READY":
                return response

        raise TimeoutError(
            f"Transactions remained NOT_READY after {max_attempts} attempts."
        )

    return _wrapper


@retry_until_transaction_ready
def get_transactions(client: PlaidApi, access_token: str) -> Any:
    return client.transactions_sync(
        TransactionsSyncRequest(
            access_token=access_token,
            count=500,
        )
    )


def extract_transactions(response: Any) -> Transactions:
    transactions = [
        Transaction(
            date=transaction.date,
            name=transaction.name,
            amount=transaction.amount,
            id=transaction.transaction_id,
        )
        for transaction in response["added"]
    ]
    return Transactions(transactions=transactions)


response = get_transactions(
    client=client,
    access_token=sandbox_token_exchange_repsonse["access_token"]
)
transactions = extract_transactions(response)
