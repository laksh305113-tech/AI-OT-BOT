from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database.session import get_db
from app.models.entities import Patient, User
from app.api.patients import patient_to_response
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.ai_assistant import generate_ai_reply

router = APIRouter(prefix="/api/ai", tags=["ai assistant"])
DbSession = Annotated[Session, Depends(get_db)]
ClinicalStaff = Annotated[User, Depends(require_roles("surgeon", "anesthetist", "nurse", "admin"))]


@router.post("/chat", response_model=AIChatResponse)
def chat_with_ai(
    payload: AIChatRequest,
    db: DbSession,
    user: ClinicalStaff,
) -> AIChatResponse:
    patient = None
    if payload.patient_id is not None:
        patient = db.get(Patient, payload.patient_id)
        if patient is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")

    patient_payload = patient_to_response(patient).model_dump() if patient is not None else None
    answer = generate_ai_reply(payload.question, patient_payload)

    return AIChatResponse(answer=answer, patient_id=payload.patient_id)
