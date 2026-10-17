from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import declarative_mixin, mapped_column, Mapped
import uuid


@declarative_mixin
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )


@declarative_mixin
class PrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
