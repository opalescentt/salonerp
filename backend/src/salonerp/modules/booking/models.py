import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from salonerp.core.db import Base


class Appointment(Base):
    __tablename__ = "appointment"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenant.id"))
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customer.id"))
    staff_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("staff.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str]


class AppointmentItem(Base):
    __tablename__ = "appointment_item"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenant.id"))
    appointment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("appointment.id"))
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("service.id"))
    duration_minutes: Mapped[int]
    sequence: Mapped[int]
