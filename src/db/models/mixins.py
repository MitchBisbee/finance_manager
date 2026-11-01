"""Provide reusable column mixins for ORM models."""

from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import declarative_mixin, mapped_column, Mapped
import uuid


@declarative_mixin
class TimestampMixin:
    """Add database-managed creation and update timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )


@declarative_mixin
class PrimaryKeyMixin:
    """Add a UUIDv7 primary key."""

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
