from abc import ABC, abstractmethod

from plaid.api.plaid_api import PlaidApi


class IPlaidSessionFactory(ABC):
    @abstractmethod
    def get_client(self) -> PlaidApi:
        """Return the existing configured Plaid API client."""

    @abstractmethod
    def get_access_token(self) -> str:
        """Return the existing access token."""
