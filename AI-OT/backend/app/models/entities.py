"""Relational schema for synthetic AI-OT prototype data only."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('admin', 'surgeon', 'anesthetist', 'nurse', 'ot_technician')", name="ck_users_role"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ai_interactions: Mapped[list[AIInteraction]] = relationship(back_populates="user")
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="user")
    device_commands: Mapped[list[DeviceCommand]] = relationship(back_populates="user")


class Patient(TimestampMixin, Base):
    __tablename__ = "patients"
    __table_args__ = (CheckConstraint("synthetic_identifier LIKE 'SYN-%'", name="ck_patients_synthetic_identifier"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    synthetic_identifier: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    patient_id: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    age: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[Optional[str]] = mapped_column(String(30), default="unknown")
    blood_group: Mapped[Optional[str]] = mapped_column(String(20))
    phone: Mapped[Optional[str]] = mapped_column(String(40))
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(200))
    medical_conditions: Mapped[Optional[str]] = mapped_column(Text)
    allergies: Mapped[Optional[str]] = mapped_column(Text)
    current_medications: Mapped[Optional[str]] = mapped_column(Text)
    previous_surgeries: Mapped[Optional[str]] = mapped_column(Text)
    previous_anesthesia_complications: Mapped[Optional[str]] = mapped_column(Text)
    family_history: Mapped[Optional[str]] = mapped_column(Text)
    additional_medical_notes: Mapped[Optional[str]] = mapped_column(Text)
    planned_procedure: Mapped[Optional[str]] = mapped_column(String(160))
    assigned_surgeon: Mapped[Optional[str]] = mapped_column(String(120))
    ot_number: Mapped[Optional[str]] = mapped_column(String(80))
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date)
    priority: Mapped[str] = mapped_column(String(30), default="routine")
    preoperative_notes: Mapped[Optional[str]] = mapped_column(Text)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sex: Mapped[Optional[str]] = mapped_column(String(20))
    medical_history: Mapped[Optional[MedicalHistory]] = relationship(back_populates="patient", uselist=False, cascade="all, delete-orphan")
    allergies_records: Mapped[list[Allergy]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    medications_records: Mapped[list[Medication]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    previous_surgeries_records: Mapped[list[PreviousSurgery]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    lab_reports: Mapped[list[LabReport]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    medical_images: Mapped[list[MedicalImage]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    surgical_sessions: Mapped[list[SurgicalSession]] = relationship(back_populates="patient", cascade="all, delete-orphan")


class MedicalHistory(TimestampMixin, Base):
    __tablename__ = "medical_history"
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), unique=True, nullable=False)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    patient: Mapped[Patient] = relationship(back_populates="medical_history")


class Allergy(TimestampMixin, Base):
    __tablename__ = "allergies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    substance: Mapped[str] = mapped_column(String(120), nullable=False)
    reaction: Mapped[Optional[str]] = mapped_column(String(255))
    patient: Mapped[Patient] = relationship(back_populates="allergies_records")


class Medication(TimestampMixin, Base):
    __tablename__ = "medications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    dosage: Mapped[Optional[str]] = mapped_column(String(80))
    patient: Mapped[Patient] = relationship(back_populates="medications_records")


class PreviousSurgery(TimestampMixin, Base):
    __tablename__ = "previous_surgeries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    procedure_name: Mapped[str] = mapped_column(String(160), nullable=False)
    performed_on: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    patient: Mapped[Patient] = relationship(back_populates="previous_surgeries_records")


class LabReport(TimestampMixin, Base):
    __tablename__ = "lab_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    report_type: Mapped[str] = mapped_column(String(120), nullable=False)
    result_summary: Mapped[str] = mapped_column(Text, nullable=False)
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    patient: Mapped[Patient] = relationship(back_populates="lab_reports")


class MedicalImage(TimestampMixin, Base):
    __tablename__ = "medical_images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False)
    modality: Mapped[str] = mapped_column(String(40), nullable=False)
    storage_reference: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_type: Mapped[str] = mapped_column(String(40), default="local", nullable=False)
    file_name: Mapped[Optional[str]] = mapped_column(String(255))
    content_type: Mapped[Optional[str]] = mapped_column(String(120))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)
    patient: Mapped[Patient] = relationship(back_populates="medical_images")


class SurgicalSession(TimestampMixin, Base):
    __tablename__ = "surgical_sessions"
    __table_args__ = (CheckConstraint("status IN ('scheduled', 'in_progress', 'completed', 'cancelled')", name="ck_sessions_status"), Index("ix_surgical_sessions_ot_status", "ot_room", "status"))
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="RESTRICT"), index=True, nullable=False)
    ot_room: Mapped[str] = mapped_column(String(40), nullable=False)
    procedure_name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="scheduled")
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    patient: Mapped[Patient] = relationship(back_populates="surgical_sessions")
    vital_signs: Mapped[list[VitalSign]] = relationship(back_populates="surgical_session", cascade="all, delete-orphan")
    alerts: Mapped[list[Alert]] = relationship(back_populates="surgical_session", cascade="all, delete-orphan")
    robot_statuses: Mapped[list[RobotStatus]] = relationship(back_populates="surgical_session", cascade="all, delete-orphan")


class VitalSign(TimestampMixin, Base):
    __tablename__ = "vital_signs"
    __table_args__ = (Index("ix_vital_signs_session_recorded", "surgical_session_id", "recorded_at"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    surgical_session_id: Mapped[int] = mapped_column(ForeignKey("surgical_sessions.id", ondelete="CASCADE"), nullable=False)
    heart_rate: Mapped[Optional[float]] = mapped_column(Float)
    spo2: Mapped[Optional[float]] = mapped_column(Float)
    blood_pressure: Mapped[Optional[str]] = mapped_column(String(30))
    respiratory_rate: Mapped[Optional[float]] = mapped_column(Float)
    temperature_c: Mapped[Optional[float]] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    surgical_session: Mapped[SurgicalSession] = relationship(back_populates="vital_signs")


class Alert(TimestampMixin, Base):
    __tablename__ = "alerts"
    __table_args__ = (CheckConstraint("severity IN ('info', 'warning', 'critical')", name="ck_alerts_severity"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    surgical_session_id: Mapped[int] = mapped_column(ForeignKey("surgical_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    surgical_session: Mapped[SurgicalSession] = relationship(back_populates="alerts")


class OTDevice(TimestampMixin, Base):
    __tablename__ = "ot_devices"
    __table_args__ = (UniqueConstraint("device_code", name="uq_ot_devices_code"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_code: Mapped[str] = mapped_column(String(80), nullable=False)
    device_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    simulation_mode: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    state: Mapped[str] = mapped_column(String(40), nullable=False, default="standby")
    commands: Mapped[list[DeviceCommand]] = relationship(back_populates="device")


class DeviceCommand(TimestampMixin, Base):
    __tablename__ = "device_commands"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    device_id: Mapped[int] = mapped_column(ForeignKey("ot_devices.id", ondelete="RESTRICT"), index=True, nullable=False)
    command_name: Mapped[str] = mapped_column(String(120), nullable=False)
    payload: Mapped[Optional[dict]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded")
    user: Mapped[User] = relationship(back_populates="device_commands")
    device: Mapped[OTDevice] = relationship(back_populates="commands")


class AIInteraction(TimestampMixin, Base):
    __tablename__ = "ai_interactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    interaction_type: Mapped[str] = mapped_column(String(80), nullable=False)
    prompt_summary: Mapped[str] = mapped_column(Text, nullable=False)
    response_summary: Mapped[Optional[str]] = mapped_column(Text)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    user: Mapped[User] = relationship(back_populates="ai_interactions")


class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_logs_user_created", "user_id", "created_at"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    action: Mapped[str] = mapped_column(String(160), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer)
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    user: Mapped[User] = relationship(back_populates="audit_logs")


class RobotStatus(TimestampMixin, Base):
    __tablename__ = "robot_status"
    __table_args__ = (Index("ix_robot_status_session_recorded", "surgical_session_id", "recorded_at"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    surgical_session_id: Mapped[int] = mapped_column(ForeignKey("surgical_sessions.id", ondelete="CASCADE"), nullable=False)
    mode: Mapped[str] = mapped_column(String(40), nullable=False, default="standby")
    connected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    surgical_session: Mapped[SurgicalSession] = relationship(back_populates="robot_statuses")
