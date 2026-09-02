from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Facility(Base):
    __tablename__ = "facility"
    __table_args__ = {"schema": "clinical"}

    facility_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    facility_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    facility_type: Mapped[str] = mapped_column(String(50), nullable=False)
    address_line_1: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state_code: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Provider(Base):
    __tablename__ = "provider"
    __table_args__ = {"schema": "clinical"}

    provider_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    facility_id: Mapped[int | None] = mapped_column(ForeignKey("clinical.facility.facility_id"))
    npi: Mapped[str | None] = mapped_column(String(10), unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    is_accepting_patients: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
