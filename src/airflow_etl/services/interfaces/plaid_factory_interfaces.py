"""Define the Plaid session factory interface."""

from abc import ABC, abstractmethod

from plaid.api.plaid_api import PlaidApi


class IPlaidSessionFactory(ABC):
    """Provide a configured Plaid client and access token."""

    @abstractmethod
    def get_client(self) -> PlaidApi:
        """Return the existing configured Plaid API client."""

    @abstractmethod
    def get_access_token(self) -> str:
        """Return the existing access token."""
