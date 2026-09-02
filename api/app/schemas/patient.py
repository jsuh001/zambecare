from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    patient_id: int
    external_patient_id: UUID
    first_name: str
    last_name: str
    date_of_birth: date
    sex_at_birth: str | None
    email: EmailStr
    phone: str | None
    preferred_language: str
    country: str
    state: str | None
    city: str | None
    postal_code: str | None
    created_at: datetime
    is_active: bool


class PatientUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    sex_at_birth: str | None = Field(default=None, max_length=20)
    phone: str | None = Field(default=None, max_length=30)
    preferred_language: str | None = Field(default=None, min_length=2, max_length=30)
    country: str | None = Field(default=None, min_length=2, max_length=56)
    state: str | None = Field(default=None, max_length=50)
    city: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
