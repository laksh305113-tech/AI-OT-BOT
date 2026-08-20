"""Pydantic models for synthetic patient management."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class PatientBase(BaseModel):
    patient_id: str = Field(..., min_length=3, max_length=80)
    name: str = Field(..., min_length=2, max_length=120)
    date_of_birth: date | None = None
    gender: str = Field(..., min_length=1, max_length=30)
    blood_group: str | None = None
    phone: str | None = None
    emergency_contact: str | None = None
    medical_conditions: str | None = None
    allergies: str | None = None
    current_medications: str | None = None
    previous_surgeries: str | None = None
    previous_anesthesia_complications: str | None = None
    family_history: str | None = None
    additional_medical_notes: str | None = None
    planned_procedure: str | None = None
    assigned_surgeon: str | None = None
    ot_number: str | None = None
    scheduled_date: date | None = None
    priority: Literal["routine", "priority", "urgent", "emergency"] = "routine"
    preoperative_notes: str | None = None
    is_archived: bool = False

    @field_validator("phone", "emergency_contact")
    @classmethod
    def normalize_contact(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        return cleaned


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    patient_id: str | None = None
    name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    phone: str | None = None
    emergency_contact: str | None = None
    medical_conditions: str | None = None
    allergies: str | None = None
    current_medications: str | None = None
    previous_surgeries: str | None = None
    previous_anesthesia_complications: str | None = None
    family_history: str | None = None
    additional_medical_notes: str | None = None
    planned_procedure: str | None = None
    assigned_surgeon: str | None = None
    ot_number: str | None = None
    scheduled_date: date | None = None
    priority: Literal["routine", "priority", "urgent", "emergency"] | None = None
    preoperative_notes: str | None = None
    is_archived: bool | None = None


class PatientRecord(PatientBase):
    id: int
    age: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    medical_history: dict[str, Any] | None = None
    allergies_list: list[dict[str, Any]] = Field(default_factory=list)
    medications: list[dict[str, Any]] = Field(default_factory=list)
    previous_surgeries_list: list[dict[str, Any]] = Field(default_factory=list)
    lab_reports: list[dict[str, Any]] = Field(default_factory=list)
    medical_images: list[dict[str, Any]] = Field(default_factory=list)
    surgical_sessions: list[dict[str, Any]] = Field(default_factory=list)
