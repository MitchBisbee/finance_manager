import os
from plaid import ApiClient, Configuration, Environment
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.api.plaid_api import PlaidApi
from finance_manager.services.interfaces.plaid_factory_interfaces import IPlaidSessionFactory


class PlaidSandboxSessionFactory(IPlaidSessionFactory):
    """Creates and retains a Plaid Sandbox client and access token."""

    def __init__(self) -> None:
        configuration = Configuration(
            host=Environment.Sandbox,
            api_key={
                "clientId": os.environ["PLAID_CLIENT_ID"],
                "secret": os.environ["PLAID_SECRET"],
            },
        )
        self._client = PlaidApi(ApiClient(configuration))

        sandbox_response = self._client.sandbox_public_token_create(
            SandboxPublicTokenCreateRequest(
                institution_id="ins_109508",
                initial_products=[Products("transactions")],
            )
        )

        token_exchange_response = self._client.item_public_token_exchange(
            ItemPublicTokenExchangeRequest(
                public_token=sandbox_response["public_token"],
            )
        )
        self._access_token: str = token_exchange_response["access_token"]

    def get_client(self) -> PlaidApi:
        """Return the existing configured client."""
        return self._client

    def get_access_token(self) -> str:
        """Return the existing access token."""
        return self._access_token
