import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import NUMERIC, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from salonerp.core.db import Base


class Service(Base):
    __tablename__ = "service"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenant.id"))
    staff_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("staff.id"))
    name: Mapped[str]
    duration_minutes: Mapped[int]
    buffer_minutes: Mapped[int]
    price: Mapped[Decimal] = mapped_column(NUMERIC(10, 2))
    description: Mapped[str | None]
    is_active: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
