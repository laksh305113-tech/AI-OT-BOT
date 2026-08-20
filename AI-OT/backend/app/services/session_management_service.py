from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SESSION_STORE: dict[int, dict[str, Any]] = {}
SESSION_EVENT_STORE: dict[int, list[dict[str, Any]]] = {}
_SESSION_SEQUENCE = 1


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_time(dt: datetime | None) -> str:
    if dt is None:
        return "--:--"
    return dt.astimezone(timezone.utc).strftime("%H:%M")


def _next_session_id() -> int:
    global _SESSION_SEQUENCE
    current = _SESSION_SEQUENCE
    _SESSION_SEQUENCE += 1
    return current


def _append_event(session_id: int, kind: str, message: str, details: dict[str, Any] | None = None) -> None:
    event = {
        "timestamp": _utc_now().isoformat(),
        "kind": kind,
        "message": message,
        "details": details or {},
    }
    SESSION_EVENT_STORE.setdefault(session_id, []).append(event)


def create_session(
    patient_id: int,
    surgeon: str,
    procedure: str,
    ot_number: str,
    status: str = "active",
    patient_name: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    session_record = {
        "id": _next_session_id(),
        "session_id": session_id or f"SESSION-{_utc_now().strftime('%Y%m%d%H%M%S')}-{_next_session_id()}",
        "patient_id": patient_id,
        "patient_name": patient_name or f"Patient #{patient_id}",
        "surgeon": surgeon,
        "procedure": procedure,
        "ot_number": ot_number,
        "start_time": _utc_now().isoformat(),
        "end_time": None,
        "status": status,
    }
    SESSION_STORE[session_record["id"]] = session_record
    SESSION_EVENT_STORE.setdefault(session_record["id"], [])
    _append_event(session_record["id"], "session", "Session started", {"status": status, "ot_number": ot_number})
    return session_record


def get_sessions() -> list[dict[str, Any]]:
    return [dict(session) for session in SESSION_STORE.values()]


def get_session(session_id: int) -> dict[str, Any] | None:
    return SESSION_STORE.get(session_id)


def get_session_events(session_id: int) -> list[dict[str, Any]]:
    return list(SESSION_EVENT_STORE.get(session_id, []))


def update_session_status(session_id: int, new_status: str) -> dict[str, Any] | None:
    session = SESSION_STORE.get(session_id)
    if session is None:
        return None
    session["status"] = new_status
    if new_status == "completed" and session.get("end_time") is None:
        session["end_time"] = _utc_now().isoformat()
    _append_event(session_id, "status", f"Session status changed to {new_status}", {"status": new_status})
    return dict(session)


def pause_session(session_id: int) -> dict[str, Any] | None:
    session = SESSION_STORE.get(session_id)
    if session is None:
        return None
    if session["status"] == "paused":
        return dict(session)
    session["status"] = "paused"
    _append_event(session_id, "status", "Session paused", {"status": "paused"})
    return dict(session)


def resume_session(session_id: int) -> dict[str, Any] | None:
    session = SESSION_STORE.get(session_id)
    if session is None:
        return None
    if session["status"] == "active":
        return dict(session)
    session["status"] = "active"
    _append_event(session_id, "status", "Session resumed", {"status": "active"})
    return dict(session)


def end_session(session_id: int) -> dict[str, Any] | None:
    session = SESSION_STORE.get(session_id)
    if session is None:
        return None
    session["status"] = "completed"
    session["end_time"] = _utc_now().isoformat()
    _append_event(session_id, "status", "Session ended", {"status": "completed"})
    return dict(session)


def record_timeline_event(session_id: int, kind: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    _append_event(session_id, kind, message, details)
    session = SESSION_STORE.get(session_id)
    if session is not None:
        return {"session_id": session["session_id"], "status": session["status"], "timeline": list(SESSION_EVENT_STORE.get(session_id, []))}
    return {"session_id": session_id, "timeline": list(SESSION_EVENT_STORE.get(session_id, []))}


def get_live_timeline(session_id: int) -> list[dict[str, Any]]:
    return list(SESSION_EVENT_STORE.get(session_id, []))
