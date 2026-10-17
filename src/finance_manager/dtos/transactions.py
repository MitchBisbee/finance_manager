from dataclasses import dataclass
from datetime import datetime


@dataclass
class ImportedTransactionDto:
    """Selected transaction data mapped from Plaid for persistence."""
    date: datetime
    name: str
    amount: float
    transaction_id: str
    category: list[str]
