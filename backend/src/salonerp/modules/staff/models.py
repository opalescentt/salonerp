import uuid
from datetime import datetime, time

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from salonerp.core.db import Base


class Staff(Base):
    __tablename__ = "staff"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenant.id"))
    first_name: Mapped[str]
    second_name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Hours(Base):
    __tablename__ = "hours"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenant.id"))
    staff_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("staff.id"))
    day_of_week: Mapped[int]
    start_time: Mapped[time]
    end_time: Mapped[time]


class TimeOff(Base):
    __tablename__ = "time_off"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenant.id"))
    staff_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("staff.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reason: Mapped[str | None]
