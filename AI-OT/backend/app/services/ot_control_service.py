from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.models.entities import AuditLog, DeviceCommand, OTDevice
from app.services.command_engine import validate_and_approve_command

EMERGENCY_STOP_ACTIVE = False
MANUAL_OVERRIDE_ENABLED = False

OT_DEVICE_LIBRARY = {
    "ot_light_1": {
        "id": "ot_light_1",
        "device_type": "surgical_light",
        "display_name": "OT Surgical Light",
        "state": {"power": True, "intensity": 70, "position": {"x": 50, "y": 50}},
        "allowed_commands": {"power", "intensity", "position"},
    },
    "camera_1": {
        "id": "camera_1",
        "device_type": "camera",
        "display_name": "Camera",
        "state": {"power": True, "zoom": 1, "focus": 50, "pan": 0, "tilt": 0, "brightness": 70},
        "allowed_commands": {"power", "zoom", "focus", "pan", "tilt", "brightness"},
    },
    "display_1": {
        "id": "display_1",
        "device_type": "display",
        "display_name": "OT Display",
        "state": {"power": True, "input_source": "main", "brightness": 75, "fullscreen": False},
        "allowed_commands": {"power", "input_source", "brightness", "fullscreen"},
    },
    "table_1": {
        "id": "table_1",
        "device_type": "operating_table",
        "display_name": "Operating Table",
        "state": {"power": True, "height": 60, "tilt": 0, "position": {"x": 50, "y": 0}},
        "allowed_commands": {"power", "height", "tilt", "position"},
    },
}

DEVICE_ROLE_RULES = {
    "ot_light_1": {"power", "intensity", "position"},
    "camera_1": {"power", "zoom", "focus", "pan", "tilt", "brightness"},
    "display_1": {"power", "input_source", "brightness", "fullscreen"},
    "table_1": {"power", "height", "tilt", "position"},
}

ROLE_ALLOWLIST = {
    "power": {"surgeon", "anesthetist", "nurse", "ot_technician", "admin"},
    "intensity": {"surgeon", "anesthetist", "nurse", "ot_technician", "admin"},
    "position": {"surgeon", "anesthetist", "nurse", "ot_technician", "admin"},
    "zoom": {"surgeon", "anesthetist", "nurse", "ot_technician", "admin"},
    "focus": {"ot_technician", "surgeon", "anesthetist", "nurse", "admin"},
    "pan": {"ot_technician", "surgeon", "anesthetist", "nurse", "admin"},
    "tilt": {"ot_technician", "surgeon", "anesthetist", "nurse", "admin"},
    "brightness": {"surgeon", "anesthetist", "nurse", "ot_technician", "admin"},
    "input_source": {"surgeon", "anesthetist", "nurse", "ot_technician", "admin"},
    "fullscreen": {"surgeon", "anesthetist", "nurse", "ot_technician", "admin"},
    "height": {"surgeon", "anesthetist", "nurse", "ot_technician", "admin"},
    "manual_override": {"surgeon", "anesthetist", "nurse", "ot_technician", "admin"},
    "emergency_stop": {"surgeon", "anesthetist", "nurse", "ot_technician", "admin"},
}

_DEVICE_STATE = {device_id: deepcopy(metadata["state"]) for device_id, metadata in OT_DEVICE_LIBRARY.items()}


def get_emergency_stop() -> bool:
    return globals()["EMERGENCY_STOP_ACTIVE"]


def set_emergency_stop(active: bool) -> bool:
    globals()["EMERGENCY_STOP_ACTIVE"] = bool(active)
    return globals()["EMERGENCY_STOP_ACTIVE"]


def get_manual_override() -> bool:
    return globals()["MANUAL_OVERRIDE_ENABLED"]


def set_manual_override(enabled: bool) -> bool:
    globals()["MANUAL_OVERRIDE_ENABLED"] = bool(enabled)
    return globals()["MANUAL_OVERRIDE_ENABLED"]


def get_ot_devices() -> list[dict[str, Any]]:
    devices = []
    for device_id, metadata in OT_DEVICE_LIBRARY.items():
        devices.append(
            {
                "id": device_id,
                "device_type": metadata["device_type"],
                "display_name": metadata["display_name"],
                "state": deepcopy(_DEVICE_STATE[device_id]),
                "allowed_commands": sorted(metadata["allowed_commands"]),
                "simulated": True,
            }
        )
    return devices


def _command_is_allowed(command_name: str, role: str) -> bool:
    return role in ROLE_ALLOWLIST.get(command_name, set())


def _validate_command_value(command_name: str, value: Any) -> tuple[bool, str | None]:
    if command_name == "power":
        if not isinstance(value, bool):
            return False, "Power state must be a boolean value."
        return True, None

    if command_name in {"intensity", "brightness", "zoom", "focus", "height", "pan", "tilt"}:
        if not isinstance(value, (int, float)):
            return False, f"{command_name} requires a numeric value."
        if command_name in {"intensity", "brightness"} and not 0 <= value <= 100:
            return False, f"{command_name} must be between 0 and 100."
        if command_name == "zoom" and not 1 <= value <= 5:
            return False, "Zoom must be between 1x and 5x."
        if command_name in {"focus", "height", "pan", "tilt"} and not -100 <= value <= 100:
            return False, f"{command_name} must be within the safe operating range."
        return True, None

    if command_name == "input_source":
        valid_sources = {"main", "overlay", "fluoroscopy", "camera"}
        if value not in valid_sources:
            return False, "Input source must be one of: main, overlay, fluoroscopy, camera."
        return True, None

    if command_name == "fullscreen":
        if not isinstance(value, bool):
            return False, "Fullscreen state must be true or false."
        return True, None

    if command_name == "manual_override":
        if not isinstance(value, bool):
            return False, "Manual override must be a boolean value."
        return True, None

    if command_name == "emergency_stop":
        if not isinstance(value, bool):
            return False, "Emergency stop must be a boolean value."
        return True, None

    if command_name == "position":
        if not isinstance(value, dict):
            return False, "Position requires an object with x and y values."
        for key in ("x", "y"):
            if key not in value or not isinstance(value[key], (int, float)):
                return False, "Position requires numeric x and y values."
        if not -100 <= value["x"] <= 100 or not -100 <= value["y"] <= 100:
            return False, "Position must stay within the simulated theatre limits."
        return True, None

    return False, f"Unsupported command: {command_name}"


def _apply_state_update(device_id: str, command_name: str, value: Any) -> None:
    state = _DEVICE_STATE[device_id]
    if command_name == "power":
        state["power"] = bool(value)
        return
    if command_name == "intensity":
        state["intensity"] = int(value)
        return
    if command_name == "brightness":
        state["brightness"] = int(value)
        return
    if command_name == "zoom":
        state["zoom"] = int(value)
        return
    if command_name == "focus":
        state["focus"] = int(value)
        return
    if command_name == "pan":
        state["pan"] = int(value)
        return
    if command_name == "tilt":
        state["tilt"] = int(value)
        return
    if command_name == "height":
        state["height"] = int(value)
        return
    if command_name == "input_source":
        state["input_source"] = str(value)
        return
    if command_name == "fullscreen":
        state["fullscreen"] = bool(value)
        return
    if command_name == "position":
        state["position"] = {"x": int(value["x"]), "y": int(value["y"])}
        return


def _to_command_result(device_id: str, command_name: str, status: str, **extra: Any) -> dict[str, Any]:
    result = {
        "status": status,
        "device": device_id,
        "command_name": command_name,
        "state": deepcopy(_DEVICE_STATE[device_id]),
    }
    result.update(extra)
    return result


def process_ot_device_command(
    device_selector: str,
    command_name: str,
    payload: dict[str, Any] | None,
    user_role: str,
    user_id: int | None = None,
    db: Any | None = None,
) -> dict[str, Any]:
    """Validate and execute a simulated OT device command with safety gating."""
    if device_selector not in _DEVICE_STATE:
        return _to_command_result(device_selector, command_name, "invalid", reason="Unknown device selector.")

    if command_name == "manual_override":
        enabled = bool((payload or {}).get("enabled", False))
        if not _command_is_allowed("manual_override", user_role):
            return _to_command_result(device_selector, command_name, "rejected", reason=f"Role '{user_role}' is not allowed to toggle manual override.")
        valid, reason = _validate_command_value("manual_override", enabled)
        if not valid:
            return _to_command_result(device_selector, command_name, "invalid", reason=reason)
        set_manual_override(enabled)
        return _to_command_result(device_selector, command_name, "approved", manual_override=get_manual_override(), reason="Manual override updated.")

    if command_name == "emergency_stop":
        enabled = bool((payload or {}).get("enabled", False))
        if not _command_is_allowed("emergency_stop", user_role):
            return _to_command_result(device_selector, command_name, "rejected", reason=f"Role '{user_role}' is not allowed to toggle emergency stop.")
        valid, reason = _validate_command_value("emergency_stop", enabled)
        if not valid:
            return _to_command_result(device_selector, command_name, "invalid", reason=reason)
        set_emergency_stop(enabled)
        return _to_command_result(device_selector, command_name, "approved", emergency_stop=get_emergency_stop(), reason="Emergency stop state updated.")

    if get_emergency_stop():
        return _to_command_result(device_selector, command_name, "emergency_stop", reason="Emergency stop is active; all simulated device commands are disabled.")

    if command_name not in OT_DEVICE_LIBRARY[device_selector]["allowed_commands"]:
        return _to_command_result(device_selector, command_name, "invalid", reason=f"Command '{command_name}' is not supported for this device.")

    if not _command_is_allowed(command_name, user_role):
        return _to_command_result(device_selector, command_name, "rejected", reason=f"Role '{user_role}' is not allowed to send '{command_name}' commands.")

    if payload is None:
        return _to_command_result(device_selector, command_name, "invalid", reason="A payload is required for this command.")

    value = payload.get(command_name)
    if value is None and command_name == "position":
        value = payload
    if value is None and command_name != "power":
        maybe_nested = payload.get("value")
        value = maybe_nested if maybe_nested is not None else payload
    valid, reason = _validate_command_value(command_name, value)
    if not valid:
        return _to_command_result(device_selector, command_name, "invalid", reason=reason)

    _apply_state_update(device_selector, command_name, value)

    if db is not None and user_id is not None:
        try:
            device_record = db.query(OTDevice).filter_by(device_code=device_selector).first()
            if device_record is not None:
                db.add(
                    DeviceCommand(
                        user_id=user_id,
                        device_id=device_record.id,
                        command_name=command_name,
                        payload=payload,
                        status="executed",
                    )
                )
            db.add(
                AuditLog(
                    user_id=user_id,
                    action="ot_device_command",
                    entity_type="ot_device",
                    entity_id=device_record.id if device_record is not None else None,
                    details={"device": device_selector, "command_name": command_name, "payload": payload},
                )
            )
            db.commit()
        except Exception:
            db.rollback()

    return _to_command_result(device_selector, command_name, "approved", reason="Simulated device command executed successfully.")


def apply_ai_command(command: dict[str, Any], user_role: str, user_id: int | None = None, db: Any | None = None) -> dict[str, Any]:
    """Translate an AI-generated intent into a validated OT device command."""
    intent = command.get("intent")
    if intent == "LIGHT_INTENSITY":
        value = command.get("value")
        return process_ot_device_command("ot_light_1", "intensity", {"intensity": value}, user_role, user_id=user_id, db=db)

    if intent == "CAMERA_ZOOM":
        value = command.get("value")
        return process_ot_device_command("camera_1", "zoom", {"zoom": value}, user_role, user_id=user_id, db=db)

    if intent == "SHOW_CAMERA":
        return {
            "status": "approved",
            "device": "camera_1",
            "command_name": "show",
            "state": deepcopy(_DEVICE_STATE["camera_1"]),
            "reason": "Camera status request accepted; this is a read-only simulated display action.",
        }

    if intent in {"PATIENT_HISTORY", "LATEST_IMAGING", "START_MONITORING", "SHOW_ROBOT_STATUS"}:
        return {
            "status": "approved",
            "device": "system",
            "command_name": intent.lower(),
            "reason": "AI command handled by the existing assistant workflow; no direct device execution performed.",
        }

    return {
        "status": "invalid",
        "reason": f"Unsupported AI command intent: {intent}",
        "device": command.get("device", "unknown"),
    }


def validate_and_execute_ai_ot_command(command: dict[str, Any], user_role: str, user_id: int | None = None, db: Any | None = None) -> dict[str, Any]:
    validation = validate_and_approve_command(command, user_role, user_id=user_id, db=db)
    if validation["status"] != "approved":
        return validation
    return apply_ai_command(command, user_role, user_id=user_id, db=db)
