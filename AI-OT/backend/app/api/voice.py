from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database.session import get_db
from app.models.entities import User
from app.schemas.voice import VoiceCommandRequest, VoiceCommandResponse
from app.services.command_engine import detect_command_intent, validate_and_approve_command

router = APIRouter(prefix="/api/voice", tags=["voice assistant"])
DbSession = Annotated[Session, Depends(get_db)]
ClinicalUser = Annotated[User, Depends(require_roles("surgeon", "anesthetist", "nurse", "ot_technician", "admin"))]


@router.post("/command", response_model=VoiceCommandResponse)
def process_voice_command(
    payload: VoiceCommandRequest,
    db: DbSession,
    user: ClinicalUser,
) -> VoiceCommandResponse:
    command = detect_command_intent(payload.text)
    validation = validate_and_approve_command(command, user.role, user.id, db)
    return VoiceCommandResponse(
        status=validation["status"],
        intent=command.get("intent", "UNKNOWN"),
        device=command.get("device", "unknown"),
        value=command.get("value"),
        reason=validation.get("reason"),
        simulated_result=validation.get("simulated_result"),
    )
