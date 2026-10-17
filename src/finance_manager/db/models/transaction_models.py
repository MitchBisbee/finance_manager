from datetime import datetime
import uuid
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey
from finance_manager.db.models.mixins import TimestampMixin, PrimaryKeyMixin
from finance_manager.db.models.base import BaseModel
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList


class Transaction(BaseModel, PrimaryKeyMixin, TimestampMixin):
    """Represents a financial transaction.

    fields:
        date (datetime): The date of the transaction.
        name (str): The name of the transaction.
        amount (float): The amount of the transaction.
        bank_transaction_id (str): The ID of the transaction in the bank's system.
    """
    __tablename__ = "transactions"
    date: Mapped[datetime] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    bank_transaction_id: Mapped[str] = mapped_column(nullable=False)


class Category(BaseModel, PrimaryKeyMixin, TimestampMixin):
    """Represents a financial transaction category.

    Fields:
        transaction_id: fk to the transaction row
        types (list[str]): The category's types.
    """

    __tablename__ = "categories"
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transactions.id"), nullable=False)
    types: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(ARRAY(String)),
        nullable=False,
        default=list,
    )
