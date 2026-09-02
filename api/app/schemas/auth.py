from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    sex_at_birth: str | None = Field(default=None, max_length=20)
    phone: str | None = Field(default=None, max_length=30)
    country: str | None = Field(default=None, min_length=2, max_length=56)
    state: str | None = Field(default=None, max_length=50)
    city: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, value: str) -> str:
        requirements = [
            any(char.islower() for char in value),
            any(char.isupper() for char in value),
            any(char.isdigit() for char in value),
            any(not char.isalnum() for char in value),
        ]
        if not all(requirements):
            raise ValueError("Password must include upper, lower, number, and symbol characters.")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    patient_id: int
    email: EmailStr
    roles: list[str]
