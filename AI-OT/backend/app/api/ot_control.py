from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database.session import get_db
from app.models.entities import User
from app.services.ot_control_service import get_ot_devices, process_ot_device_command

router = APIRouter(prefix="/api/ot", tags=["ot control center"])
DbSession = Annotated[Session, Depends(get_db)]
ClinicalUser = Annotated[User, Depends(require_roles("surgeon", "anesthetist", "nurse", "ot_technician", "admin"))]


class OTDeviceCommandRequest(BaseModel):
    command: str = Field(..., min_length=1, max_length=80)
    payload: dict[str, object] | None = None


@router.get("/devices")
def list_ot_devices(db: DbSession, user: ClinicalUser) -> dict[str, object]:
    _ = db
    _ = user
    return {"devices": get_ot_devices(), "simulation_mode": True, "emergency_stop": False}


@router.post("/devices/{device_id}/command")
def send_ot_device_command(
    device_id: str,
    payload: OTDeviceCommandRequest,
    db: DbSession,
    user: ClinicalUser,
) -> dict[str, object]:
    command_name = payload.command.strip()
    result = process_ot_device_command(
        device_selector=device_id,
        command_name=command_name,
        payload=payload.payload or {},
        user_role=user.role,
        user_id=user.id,
        db=db,
    )
    if result["status"] in {"invalid", "rejected", "emergency_stop"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)
    return result
