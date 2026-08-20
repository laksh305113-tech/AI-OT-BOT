"""Prototype-only endpoints demonstrating server-side authorization."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.dependencies import require_roles
from app.models.entities import User

router = APIRouter(prefix="/api", tags=["protected prototype modules"])

SURGEON = ("surgeon",)
CLINICAL_TEAM = ("surgeon", "anesthetist", "nurse")


def protected_message(module: str, user: User) -> dict[str, str]:
    return {"module": module, "message": "Authorized prototype placeholder; no clinical or device action is performed.", "role": user.role}


@router.get("/monitoring")
def monitoring(user: Annotated[User, Depends(require_roles(*CLINICAL_TEAM))]):
    return protected_message("monitoring", user)


@router.get("/alerts")
def alerts(user: Annotated[User, Depends(require_roles(*CLINICAL_TEAM))]):
    return protected_message("alerts", user)


@router.get("/imaging")
def imaging(user: Annotated[User, Depends(require_roles(*SURGEON))]):
    return protected_message("imaging", user)


@router.get("/ai-assistant")
def ai_assistant(user: Annotated[User, Depends(require_roles(*SURGEON))]):
    return protected_message("AI assistant", user)


@router.get("/camera")
def camera(user: Annotated[User, Depends(require_roles("surgeon", "ot_technician"))]):
    return protected_message("camera", user)


@router.get("/ot-control")
def ot_control(user: Annotated[User, Depends(require_roles("surgeon", "nurse"))]):
    return protected_message("OT controls", user)


@router.get("/robot")
def robot(user: Annotated[User, Depends(require_roles(*SURGEON))]):
    return protected_message("robot simulator", user)


@router.get("/devices")
def devices(user: Annotated[User, Depends(require_roles("ot_technician"))]):
    return protected_message("equipment status", user)


@router.get("/admin/users")
def users(user: Annotated[User, Depends(require_roles("admin"))]):
    return protected_message("user administration", user)


@router.get("/admin/audit-logs")
def audit_logs(user: Annotated[User, Depends(require_roles("admin"))]):
    return protected_message("audit logs", user)


@router.get("/admin/configuration")
def configuration(user: Annotated[User, Depends(require_roles("admin"))]):
    return protected_message("configuration", user)
