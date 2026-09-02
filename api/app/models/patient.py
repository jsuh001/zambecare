from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.identity import UserAccount


class Patient(Base):
    __tablename__ = "patient"
    __table_args__ = {"schema": "clinical"}

    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("security.user_account.user_id"), unique=True, nullable=True
    )
    external_patient_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), unique=True, default=uuid4, nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    sex_at_birth: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    preferred_language: Mapped[str] = mapped_column(String(30), default="English", nullable=False)
    country: Mapped[str] = mapped_column(
        String(56), default="United States", server_default="United States", nullable=False
    )
    state: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str | None] = mapped_column(String(100))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped[UserAccount | None] = relationship(back_populates="patient")
