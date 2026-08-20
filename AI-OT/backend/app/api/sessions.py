from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database.session import get_db
from app.models.entities import Patient, User
from app.services.session_management_service import (
    create_session,
    get_live_timeline,
    get_session,
    get_sessions,
    pause_session,
    record_timeline_event,
    resume_session,
    end_session,
)

router = APIRouter(prefix="/api/sessions", tags=["surgical sessions"])
DbSession = Annotated[Session, Depends(get_db)]
ClinicalUser = Annotated[User, Depends(require_roles("surgeon", "anesthetist", "nurse", "ot_technician", "admin"))]


class SessionCreateRequest(BaseModel):
    patient_id: int = Field(..., ge=1)
    surgeon: str = Field(..., min_length=1, max_length=120)
    procedure: str = Field(..., min_length=1, max_length=200)
    ot_number: str = Field(..., min_length=1, max_length=80)
    status: str = Field(default="active")


class SessionActionRequest(BaseModel):
    event: str = Field(..., min_length=1, max_length=80)
    details: dict[str, Any] | None = None


@router.get("")
def list_sessions(db: DbSession, user: ClinicalUser) -> dict[str, Any]:
    _ = db
    _ = user
    return {"sessions": get_sessions()}


@router.post("")
def create_surgical_session(payload: SessionCreateRequest, db: DbSession, user: ClinicalUser) -> dict[str, Any]:
    patient = db.get(Patient, payload.patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    session = create_session(
        patient_id=payload.patient_id,
        surgeon=payload.surgeon,
        procedure=payload.procedure,
        ot_number=payload.ot_number,
        status=payload.status,
        patient_name=patient.display_name,
    )
    record_timeline_event(session["id"], "session", "Session created", {"created_by": user.display_name})
    return session


@router.get("/{session_id}")
def get_surgical_session(session_id: int, db: DbSession, user: ClinicalUser) -> dict[str, Any]:
    _ = db
    _ = user
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    session["timeline"] = get_live_timeline(session_id)
    return session


@router.post("/{session_id}/pause")
def pause_surgical_session(session_id: int, db: DbSession, user: ClinicalUser) -> dict[str, Any]:
    _ = db
    _ = user
    session = pause_session(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return session


@router.post("/{session_id}/resume")
def resume_surgical_session(session_id: int, db: DbSession, user: ClinicalUser) -> dict[str, Any]:
    _ = db
    _ = user
    session = resume_session(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return session


@router.post("/{session_id}/end")
def end_surgical_session(session_id: int, db: DbSession, user: ClinicalUser) -> dict[str, Any]:
    _ = db
    _ = user
    session = end_session(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return session


@router.post("/{session_id}/events")
def record_session_event(session_id: int, payload: SessionActionRequest, db: DbSession, user: ClinicalUser) -> dict[str, Any]:
    _ = db
    _ = user
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return record_timeline_event(session_id, payload.event, payload.event, payload.details)
