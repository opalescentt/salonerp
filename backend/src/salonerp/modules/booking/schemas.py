import datetime as dt
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateAppointmentItemRequest(BaseModel):
    service_id: UUID


class CreateAppointmentRequest(BaseModel):
    customer_id: UUID
    staff_id: UUID
    started_at: dt.datetime
    items: list[CreateAppointmentItemRequest] = Field(min_length=1)

    @field_validator("started_at")
    @classmethod
    def validate_started_at(cls, value: dt.datetime) -> dt.datetime:
        if value.tzinfo is None:
            raise ValueError("started_at must include a timezone")
        if value < dt.datetime.now(dt.UTC):
            raise ValueError("started_at must not be in the past")
        return value


class AppointmentItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    appointment_id: UUID
    service_id: UUID
    duration_minutes: int
    sequence: int


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    customer_id: UUID
    staff_id: UUID
    started_at: dt.datetime
    end_at: dt.datetime
    created_at: dt.datetime
    status: str
    items: list[AppointmentItemResponse]