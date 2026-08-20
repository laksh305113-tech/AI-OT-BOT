"""Safety-first command parser and validator for voice-driven OT assistance."""

from __future__ import annotations

import re
from typing import Any

ALLOWED_ROLES = {
    "PATIENT_HISTORY": {"surgeon", "anesthetist", "nurse", "admin"},
    "LATEST_IMAGING": {"surgeon", "anesthetist", "nurse", "admin"},
    "START_MONITORING": {"surgeon", "anesthetist", "nurse", "admin"},
    "SHOW_CAMERA": {"surgeon", "anesthetist", "nurse", "ot_technician"},
    "CAMERA_ZOOM": {"surgeon", "anesthetist", "nurse", "ot_technician"},
    "LIGHT_INTENSITY": {"surgeon", "anesthetist", "nurse", "ot_technician"},
    "SHOW_ROBOT_STATUS": {"surgeon", "anesthetist"},
}


def _clean_text(text: str) -> str:
    return (text or "").strip()


def _extract_number(candidate: str | None) -> int | None:
    if candidate is None:
        return None
    match = re.search(r"(\d+)", candidate)
    if not match:
        return None
    return int(match.group(1))


def detect_command_intent(raw_text: str) -> dict[str, Any]:
    """Map a user command to a structured intent and target device."""
    text = _clean_text(raw_text).lower()
    if not text:
        return {"intent": "UNKNOWN", "device": "unknown", "value": None, "raw": raw_text}

    if "show patient history" in text or "patient history" in text:
        return {"intent": "PATIENT_HISTORY", "device": "patient_record", "value": None, "raw": raw_text}

    if "latest x-ray" in text or "latest xray" in text or "latest imaging" in text:
        return {"intent": "LATEST_IMAGING", "device": "imaging_xray", "value": None, "raw": raw_text}

    if "start monitoring" in text or "start monitor" in text:
        return {"intent": "START_MONITORING", "device": "monitoring", "value": None, "raw": raw_text}

    if "show robot status" in text or "robot status" in text:
        return {"intent": "SHOW_ROBOT_STATUS", "device": "robot_status", "value": None, "raw": raw_text}

    if "show camera" in text or "camera" in text and "zoom" not in text:
        match = re.search(r"camera\s*(\d+)", text)
        device = f"camera_{match.group(1)}" if match else "camera_1"
        return {"intent": "SHOW_CAMERA", "device": device, "value": None, "raw": raw_text}

    if "zoom camera" in text:
        match = re.search(r"camera\s*(\d+)", text)
        device = f"camera_{match.group(1)}" if match else "camera_1"
        value = _extract_number(text.replace("camera", " "))
        if value is None:
            value = 2
        return {"intent": "CAMERA_ZOOM", "device": device, "value": value, "raw": raw_text}

    if "light intensity" in text or "ot light" in text:
        device = "ot_light_1"
        value = _extract_number(text)
        if value is None:
            value = 50
        return {"intent": "LIGHT_INTENSITY", "device": device, "value": value, "raw": raw_text}

    return {"intent": "UNKNOWN", "device": "unknown", "value": None, "raw": raw_text}


def _validate_value(command: dict[str, Any]) -> tuple[bool, str | None]:
    intent = command.get("intent")
    value = command.get("value")

    if intent == "CAMERA_ZOOM":
        if value is None or not isinstance(value, (int, float)):
            return False, "Camera zoom requires a numeric value."
        if value < 1 or value > 5:
            return False, "Camera zoom must be between 1x and 5x."
        return True, None

    if intent == "LIGHT_INTENSITY":
        if value is None or not isinstance(value, (int, float)):
            return False, "Light intensity requires a numeric percentage."
        if value < 0 or value > 100:
            return False, "Light intensity must be between 0 and 100 percent."
        return True, None

    return True, None


def validate_and_approve_command(command: dict[str, Any], user_role: str, user_id: int | None = None, db: Any | None = None) -> dict[str, Any]:
    """Validate intent, role permission, and simulated safety constraints."""
    if not isinstance(command, dict):
        return {"status": "invalid", "reason": "Command must be a structured object.", "simulated_result": {"executed": False}}

    intent = command.get("intent")
    device = command.get("device")
    if intent is None or device is None:
        return {"status": "invalid", "reason": "Command is missing intent or device.", "simulated_result": {"executed": False}}

    if intent not in ALLOWED_ROLES:
        return {"status": "invalid", "reason": f"Unsupported command intent: {intent}", "simulated_result": {"executed": False}}

    allowed_roles = ALLOWED_ROLES[intent]
    if user_role not in allowed_roles:
        return {
            "status": "rejected",
            "reason": f"User role '{user_role}' is not authorized for {intent}.",
            "simulated_result": {"executed": False, "device": device, "status": "rejected"},
        }

    valid, reason = _validate_value(command)
    if not valid:
        return {"status": "invalid", "reason": reason, "simulated_result": {"executed": False, "device": device, "status": "invalid"}}

    result = {
        "status": "approved",
        "intent": intent,
        "device": device,
        "value": command.get("value"),
        "simulated_result": {
            "executed": True,
            "device": device,
            "status": "simulated",
            "message": f"{intent} command captured for {device} in simulation mode.",
        },
    }

    if db is not None and user_id is not None:
        try:
            from app.models.entities import AuditLog

            db.add(
                AuditLog(
                    user_id=user_id,
                    action="voice_command",
                    entity_type="command",
                    entity_id=None,
                    details={
                        "intent": intent,
                        "device": device,
                        "value": command.get("value"),
                        "status": "approved",
                    },
                )
            )
            db.commit()
        except Exception:
            db.rollback()

    return result
