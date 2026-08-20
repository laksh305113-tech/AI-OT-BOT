"""Safety-first AI assistant service for patient context responses."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import request, error

from app.config import get_settings

NO_INFO = "No information is available in the patient's records."


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _clean_multiline(value: Any) -> str:
    text = _as_text(value)
    if not text:
        return NO_INFO
    return text


def _safe_join(values: list[str]) -> str:
    items = [item.strip() for item in values if item and item.strip()]
    if not items:
        return NO_INFO
    return "; ".join(items)


def build_patient_context(patient: dict[str, Any] | Any) -> dict[str, str]:
    """Translate a patient record into a compact, safe context for LLM prompts."""
    if patient is None:
        return {
            "summary": "No patient context is available.",
            "allergies": NO_INFO,
            "medications": NO_INFO,
            "previous_surgeries": NO_INFO,
            "planned_procedure": NO_INFO,
            "latest_imaging": NO_INFO,
            "medical_conditions": NO_INFO,
            "preoperative_notes": NO_INFO,
        }

    if not isinstance(patient, dict):
        patient = {
            "patient_id": getattr(patient, "patient_id", None),
            "name": getattr(patient, "name", None),
            "age": getattr(patient, "age", None),
            "gender": getattr(patient, "gender", None),
            "blood_group": getattr(patient, "blood_group", None),
            "allergies": getattr(patient, "allergies", None),
            "current_medications": getattr(patient, "current_medications", None),
            "previous_surgeries": getattr(patient, "previous_surgeries", None),
            "planned_procedure": getattr(patient, "planned_procedure", None),
            "assigned_surgeon": getattr(patient, "assigned_surgeon", None),
            "ot_number": getattr(patient, "ot_number", None),
            "scheduled_date": getattr(patient, "scheduled_date", None),
            "medical_conditions": getattr(patient, "medical_conditions", None),
            "preoperative_notes": getattr(patient, "preoperative_notes", None),
            "medical_images": getattr(patient, "medical_images", None),
        }

    patient_id = _as_text(patient.get("patient_id"))
    name = _as_text(patient.get("name"))
    age = patient.get("age")
    gender = _as_text(patient.get("gender"))
    blood_group = _as_text(patient.get("blood_group"))
    allergies = _clean_multiline(patient.get("allergies"))
    medications = _clean_multiline(patient.get("current_medications"))
    previous_surgeries = _clean_multiline(patient.get("previous_surgeries"))
    planned_procedure = _clean_multiline(patient.get("planned_procedure"))
    assigned_surgeon = _clean_multiline(patient.get("assigned_surgeon"))
    ot_number = _clean_multiline(patient.get("ot_number"))
    scheduled_date = _as_text(patient.get("scheduled_date"))
    medical_conditions = _clean_multiline(patient.get("medical_conditions"))
    preoperative_notes = _clean_multiline(patient.get("preoperative_notes"))

    image_items = patient.get("medical_images") or []
    image_summary = NO_INFO
    if isinstance(image_items, list) and image_items:
        image_summary = "; ".join(
            [
                item.get("modality", "Medical image") + (f" - {item.get('description') or item.get('storage_reference', '')}" if item.get("description") or item.get("storage_reference") else "")
                for item in image_items
                if isinstance(item, dict)
            ]
        )

    summary_parts = [f"Patient {name or 'Unknown'} ({patient_id or 'No ID'})."]
    if age is not None:
        summary_parts.append(f"Age: {age}.")
    if gender:
        summary_parts.append(f"Gender: {gender}.")
    if blood_group:
        summary_parts.append(f"Blood group: {blood_group}.")
    if planned_procedure != NO_INFO:
        summary_parts.append(f"Planned procedure: {planned_procedure}.")
    if assigned_surgeon != NO_INFO:
        summary_parts.append(f"Assigned surgeon: {assigned_surgeon}.")
    if ot_number != NO_INFO:
        summary_parts.append(f"OT number: {ot_number}.")
    if scheduled_date:
        summary_parts.append(f"Scheduled date: {scheduled_date}.")

    return {
        "summary": " ".join(summary_parts),
        "allergies": allergies,
        "medications": medications,
        "previous_surgeries": previous_surgeries,
        "planned_procedure": planned_procedure,
        "latest_imaging": image_summary,
        "medical_conditions": medical_conditions,
        "preoperative_notes": preoperative_notes,
    }


def _format_prompt(question: str, patient_context: dict[str, str]) -> str:
    return f"""You are a clinical AI assistant prototype for a hospital operating theatre dashboard.
Safety rules:
- Use only information from the provided patient context.
- Never invent patient information.
- Never diagnose independently.
- Never prescribe treatment.
- Never make autonomous surgical decisions.
- Never directly control physical equipment.
- If information is missing, respond with: "No information is available in the patient's records."

Patient context:
- Summary: {patient_context['summary']}
- Allergies: {patient_context['allergies']}
- Medications: {patient_context['medications']}
- Previous surgeries: {patient_context['previous_surgeries']}
- Planned procedure: {patient_context['planned_procedure']}
- Latest imaging: {patient_context['latest_imaging']}
- Medical conditions: {patient_context['medical_conditions']}
- Preoperative notes: {patient_context['preoperative_notes']}

User question: {question}

Provide a concise answer using only the above information. Do not mention the safety rules or the prompt itself.
"""


def generate_local_reply(question: str, patient: dict[str, Any] | None) -> str:
    normalized = (question or "").lower()
    context = build_patient_context(patient)

    if "allerg" in normalized:
        return context["allergies"]
    if "medication" in normalized:
        return context["medications"]
    if "surgery" in normalized:
        return context["previous_surgeries"]
    if "imaging" in normalized or "image" in normalized:
        return context["latest_imaging"]
    if "summar" in normalized:
        return context["summary"]
    if "condition" in normalized:
        return context["medical_conditions"]
    if "preoperative" in normalized or "notes" in normalized:
        return context["preoperative_notes"]

    if patient is None:
        return "No current patient is selected. No information is available in the patient's records."

    return f"{context['summary']} {context['allergies']}"


def _call_openai_compatible_model(question: str, patient_context: dict[str, str]) -> str:
    settings = get_settings()
    api_key = (settings.ai_api_key or os.getenv("AI_API_KEY") or "").strip()
    if not api_key:
        return generate_local_reply(question, patient_context)

    payload = {
        "model": settings.ai_model or os.getenv("AI_MODEL") or "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a safe clinical assistant prototype. Use only provided patient context and never invent missing information."},
            {"role": "user", "content": _format_prompt(question, patient_context)},
        ],
        "temperature": 0.2,
        "max_tokens": 250,
    }

    url = settings.ai_api_base_url or os.getenv("AI_API_BASE_URL") or "https://api.openai.com/v1/chat/completions"
    data = json.dumps(payload).encode("utf-8")
    request_obj = request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }, method="POST")

    try:
        with request.urlopen(request_obj, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (error.HTTPError, error.URLError, TimeoutError, ValueError):
        return generate_local_reply(question, patient_context)

    choices = body.get("choices") or []
    if not choices:
        return generate_local_reply(question, patient_context)

    message = choices[0].get("message", {}).get("content", "")
    return message.strip() or generate_local_reply(question, patient_context)


def generate_ai_reply(question: str, patient: dict[str, Any] | None) -> str:
    """Return a safe answer using local fallback or the configured AI provider."""
    patient_context = build_patient_context(patient)
    return _call_openai_compatible_model(question, patient_context)
