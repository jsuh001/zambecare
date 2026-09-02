from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class FacilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    facility_id: int
    facility_name: str
    facility_type: str
    address_line_1: str
    city: str
    state_code: str
    postal_code: str
    latitude: Decimal | None
    longitude: Decimal | None
    is_active: bool


class ProviderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    provider_id: int
    facility_id: int | None
    npi: str | None
    first_name: str
    last_name: str
    specialty_code: str
    is_accepting_patients: bool


class FacilityCreate(BaseModel):
    facility_name: str = Field(min_length=2, max_length=200)
    facility_type: str = Field(min_length=2, max_length=50)
    address_line_1: str = Field(min_length=2, max_length=200)
    city: str = Field(min_length=2, max_length=100)
    state_code: str = Field(min_length=2, max_length=2)
    postal_code: str = Field(min_length=5, max_length=10)


class ProviderCreate(BaseModel):
    facility_id: int | None = None
    npi: str | None = Field(default=None, min_length=10, max_length=10)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    specialty_code: str = Field(min_length=2, max_length=50)
    is_accepting_patients: bool = True
