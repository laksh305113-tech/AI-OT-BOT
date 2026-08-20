"""Synthetic patient management endpoints."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.config import get_settings
from app.database.session import get_db
from app.models.entities import MedicalImage, Patient, User
from app.schemas.patient import PatientCreate, PatientRecord, PatientUpdate
from app.services.imaging_service import save_uploaded_patient_image

router = APIRouter(prefix="/api/patients", tags=["patients"])
DbSession = Annotated[Session, Depends(get_db)]
ClinicalTeam = Annotated[User, Depends(require_roles("surgeon", "anesthetist", "nurse", "admin"))]


def patient_to_response(patient: Patient) -> PatientRecord:
    age = None
    if patient.date_of_birth:
        today = date.today()
        age = today.year - patient.date_of_birth.year - ((today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day))

    image_records = []
    for image in patient.medical_images or []:
        image_records.append({
            "id": image.id,
            "patient_id": patient.id,
            "modality": image.modality,
            "storage_reference": image.storage_reference,
            "storage_type": image.storage_type,
            "file_name": image.file_name,
            "content_type": image.content_type,
            "description": image.description,
            "file_size": image.file_size,
            "url": f"/api/patients/{patient.id}/images/{image.id}/file",
        })

    return PatientRecord(
        id=patient.id,
        patient_id=patient.patient_id,
        name=patient.name,
        date_of_birth=patient.date_of_birth,
        age=age,
        gender=patient.gender or "unknown",
        blood_group=patient.blood_group,
        phone=patient.phone,
        emergency_contact=patient.emergency_contact,
        medical_conditions=patient.medical_conditions,
        allergies=patient.allergies,
        current_medications=patient.current_medications,
        previous_surgeries=patient.previous_surgeries,
        previous_anesthesia_complications=patient.previous_anesthesia_complications,
        family_history=patient.family_history,
        additional_medical_notes=patient.additional_medical_notes,
        planned_procedure=patient.planned_procedure,
        assigned_surgeon=patient.assigned_surgeon,
        ot_number=patient.ot_number,
        scheduled_date=patient.scheduled_date,
        priority=patient.priority,
        preoperative_notes=patient.preoperative_notes,
        is_archived=patient.is_archived,
        medical_history={"summary": patient.medical_conditions or "No medical history recorded."},
        allergies_list=[{"name": item} for item in (patient.allergies or "").split("\n") if item.strip()],
        medications=[{"name": item} for item in (patient.current_medications or "").split("\n") if item.strip()],
        previous_surgeries_list=[{"name": item} for item in (patient.previous_surgeries or "").split("\n") if item.strip()],
        lab_reports=[],
        medical_images=image_records,
        surgical_sessions=[],
        created_at=patient.created_at,
        updated_at=patient.updated_at,
    )


@router.get("", response_model=list[PatientRecord])
def list_patients(
    db: DbSession,
    user: ClinicalTeam,
    search: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    gender: str | None = Query(default=None),
    archived: bool | None = Query(default=False),
) -> list[PatientRecord]:
    query = select(Patient)

    if not archived:
        query = query.where(Patient.is_archived.is_(False))

    if search:
        term = f"%{search.lower()}%"
        query = query.where(
            or_(
                Patient.patient_id.ilike(term),
                Patient.name.ilike(term),
                Patient.assigned_surgeon.ilike(term),
                Patient.planned_procedure.ilike(term),
            )
        )

    if priority:
        query = query.where(Patient.priority == priority)

    if gender:
        query = query.where(Patient.gender == gender)

    patients = db.scalars(query.order_by(Patient.created_at.desc())).all()
    return [patient_to_response(patient) for patient in patients]


@router.post("", response_model=PatientRecord, status_code=status.HTTP_201_CREATED)
def create_patient(
    payload: PatientCreate,
    db: DbSession,
    user: ClinicalTeam,
) -> PatientRecord:
    existing = db.scalar(select(Patient).where(Patient.patient_id == payload.patient_id))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient ID already exists.")

    patient = Patient(
        synthetic_identifier=f"SYN-{payload.patient_id.strip().upper()}",
        display_name=payload.name,
        patient_id=payload.patient_id.strip(),
        name=payload.name.strip(),
        date_of_birth=payload.date_of_birth,
        age=None,
        gender=payload.gender.strip(),
        blood_group=payload.blood_group.strip() if payload.blood_group else None,
        phone=payload.phone.strip() if payload.phone else None,
        emergency_contact=payload.emergency_contact.strip() if payload.emergency_contact else None,
        medical_conditions=payload.medical_conditions.strip() if payload.medical_conditions else None,
        allergies=payload.allergies.strip() if payload.allergies else None,
        current_medications=payload.current_medications.strip() if payload.current_medications else None,
        previous_surgeries=payload.previous_surgeries.strip() if payload.previous_surgeries else None,
        previous_anesthesia_complications=payload.previous_anesthesia_complications.strip() if payload.previous_anesthesia_complications else None,
        family_history=payload.family_history.strip() if payload.family_history else None,
        additional_medical_notes=payload.additional_medical_notes.strip() if payload.additional_medical_notes else None,
        planned_procedure=payload.planned_procedure.strip() if payload.planned_procedure else None,
        assigned_surgeon=payload.assigned_surgeon.strip() if payload.assigned_surgeon else None,
        ot_number=payload.ot_number.strip() if payload.ot_number else None,
        scheduled_date=payload.scheduled_date,
        priority=payload.priority,
        preoperative_notes=payload.preoperative_notes.strip() if payload.preoperative_notes else None,
        is_archived=payload.is_archived,
    )

    if patient.date_of_birth:
        today = date.today()
        patient.age = today.year - patient.date_of_birth.year - ((today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day))

    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient_to_response(patient)


@router.get("/{patient_id}", response_model=PatientRecord)
def get_patient(patient_id: int, db: DbSession, user: ClinicalTeam) -> PatientRecord:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    return patient_to_response(patient)


@router.put("/{patient_id}", response_model=PatientRecord)
def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    db: DbSession,
    user: ClinicalTeam,
) -> PatientRecord:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")

    update_data = payload.model_dump(exclude_unset=True)
    if payload.patient_id is not None:
        existing = db.scalar(select(Patient).where(Patient.patient_id == payload.patient_id, Patient.id != patient_id))
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient ID already exists.")

    for field, value in update_data.items():
        if value is not None and field not in {"patient_id"}:
            setattr(patient, field, value)

    if payload.patient_id is not None:
        patient.patient_id = payload.patient_id.strip()
        patient.synthetic_identifier = f"SYN-{payload.patient_id.strip().upper()}"
        patient.display_name = patient.name or patient.display_name

    if payload.name is not None:
        patient.name = payload.name.strip()
        patient.display_name = patient.name

    if payload.date_of_birth is not None:
        today = date.today()
        patient.age = today.year - payload.date_of_birth.year - ((today.month, today.day) < (payload.date_of_birth.month, payload.date_of_birth.day))

    if payload.gender is not None:
        patient.gender = payload.gender.strip()

    db.commit()
    db.refresh(patient)
    return patient_to_response(patient)


@router.get("/{patient_id}/images", response_model=list[dict])
def list_patient_images(
    patient_id: int,
    db: DbSession,
    user: ClinicalTeam,
) -> list[dict]:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")

    images = []
    for image in patient.medical_images:
        images.append({
            "id": image.id,
            "patient_id": patient.id,
            "modality": image.modality,
            "description": image.description,
            "file_name": image.file_name,
            "content_type": image.content_type,
            "file_size": image.file_size,
            "storage_type": image.storage_type,
            "storage_reference": image.storage_reference,
            "url": f"/api/patients/{patient.id}/images/{image.id}/file",
        })
    return images


@router.post("/{patient_id}/images", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_patient_image(
    patient_id: int,
    file: Annotated[UploadFile, File(...)],
    modality: str = Form("XRAY"),
    description: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("surgeon", "anesthetist", "nurse", "admin")),
) -> dict:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")

    saved = await save_uploaded_patient_image(db, patient, file, modality=modality, description=description)
    return {
        "id": saved.id,
        "patient_id": patient.id,
        "modality": saved.modality,
        "description": saved.description,
        "file_name": saved.file_name,
        "content_type": saved.content_type,
        "file_size": saved.file_size,
        "storage_type": saved.storage_type,
        "storage_reference": saved.storage_reference,
        "url": f"/api/patients/{patient.id}/images/{saved.id}/file",
    }


@router.get("/{patient_id}/images/{image_id}/file")
def get_patient_image_file(
    patient_id: int,
    image_id: int,
    db: DbSession,
    user: ClinicalTeam,
) -> FileResponse:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    image = db.get(MedicalImage, image_id)
    if image is None or image.patient_id != patient_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")

    storage_path = Path(get_settings().image_storage_path).resolve() / image.storage_reference
    if not storage_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file not found on disk.")
    return FileResponse(storage_path, media_type=image.content_type or "application/octet-stream", filename=image.file_name or image.storage_reference)


@router.delete("/{patient_id}", status_code=status.HTTP_200_OK)
def archive_patient(patient_id: int, db: DbSession, user: ClinicalTeam) -> dict[str, str]:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    patient.is_archived = True
    db.commit()
    return {"status": "archived", "patient_id": str(patient_id)}
