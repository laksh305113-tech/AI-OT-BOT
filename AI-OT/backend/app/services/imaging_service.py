from __future__ import annotations

from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.entities import MedicalImage, Patient


ALLOWED_IMAGE_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}


async def save_uploaded_patient_image(db: Session, patient: Patient, file: UploadFile, *, modality: str, description: str | None) -> MedicalImage:
    suffix = Path(file.filename or "upload.bin").suffix.lower()
    allowed_suffixes = {".png", ".jpg", ".jpeg"}
    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES and suffix not in allowed_suffixes:
        raise ValueError("Unsupported image format. PNG, JPG, and JPEG are supported for this prototype.")

    storage_root = Path(get_settings().image_storage_path).resolve()
    storage_root.mkdir(parents=True, exist_ok=True)

    safe_name = f"patient-{patient.id}-{file.filename or 'upload'}".replace("/", "_").replace("\\", "_")
    target_path = storage_root / safe_name
    contents = await file.read()
    target_path.write_bytes(contents)

    image = MedicalImage(
        patient_id=patient.id,
        modality=(modality or "XRAY").strip().upper()[:40],
        storage_reference=safe_name,
        storage_type="local",
        file_name=file.filename or safe_name,
        content_type=file.content_type or "application/octet-stream",
        file_size=len(contents),
        description=description.strip() if description else None,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image
