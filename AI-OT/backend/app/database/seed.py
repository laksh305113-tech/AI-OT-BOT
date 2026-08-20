"""Idempotent seed data for local AI-OT demonstrations.

Every record in this module is fictional and synthetic; it must never be
replaced with information from real patients or real OT equipment.
"""
from datetime import UTC, datetime

from sqlalchemy import select

from app.database.init_db import initialize_database
from app.database.session import SessionLocal
from app.auth.security import hash_password
from app.config import get_settings
from app.models.entities import (
    AIInteraction,
    Alert,
    Allergy,
    AuditLog,
    DeviceCommand,
    LabReport,
    MedicalHistory,
    MedicalImage,
    Medication,
    OTDevice,
    Patient,
    PreviousSurgery,
    RobotStatus,
    SurgicalSession,
    User,
    VitalSign,
)


def seed_database() -> None:
    initialize_database()
    with SessionLocal() as db:
        if db.scalar(select(User.id).limit(1)):
            print("Seed data already exists; no records added.")
            return

        password_hash = hash_password(get_settings().demo_seed_password)
        admin = User(email="admin@aiot-demo.com", display_name="Avery Admin", role="admin", password_hash=password_hash)
        surgeon = User(email="surgeon@aiot-demo.com", display_name="Sam Surgeon", role="surgeon", password_hash=password_hash)
        anesthetist = User(email="anesthetist@aiot-demo.com", display_name="Alex Anesthetist", role="anesthetist", password_hash=password_hash)
        nurse = User(email="nurse@aiot-demo.com", display_name="Noor Nurse", role="nurse", password_hash=password_hash)
        technician = User(email="technician@aiot-demo.com", display_name="Taylor Technician", role="ot_technician", password_hash=password_hash)
        patients = [
            Patient(synthetic_identifier="SYN-PT-001", display_name="Synthetic Patient Alpha", date_of_birth=datetime(1988, 4, 10).date(), sex="unspecified"),
            Patient(synthetic_identifier="SYN-PT-002", display_name="Synthetic Patient Beta", date_of_birth=datetime(1976, 9, 22).date(), sex="unspecified"),
            Patient(synthetic_identifier="SYN-PT-003", display_name="Synthetic Patient Gamma", date_of_birth=datetime(1994, 1, 5).date(), sex="unspecified"),
        ]
        db.add_all([admin, surgeon, anesthetist, nurse, technician, *patients])
        db.flush()

        alpha = patients[0]
        db.add_all([
            MedicalHistory(patient=alpha, summary="Synthetic demonstration history only; not clinical data."),
            Allergy(patient=alpha, substance="Synthetic example allergen", reaction="Synthetic example reaction"),
            Medication(patient=alpha, name="Synthetic sample medication", dosage="Example only"),
            PreviousSurgery(patient=alpha, procedure_name="Synthetic prior procedure", notes="Demonstration record only"),
            LabReport(patient=alpha, report_type="Synthetic lab panel", result_summary="Demo values only; no clinical interpretation."),
            MedicalImage(patient=alpha, modality="SIM", storage_reference="synthetic://images/alpha-001", description="Synthetic image placeholder"),
        ])

        session = SurgicalSession(
            patient=alpha,
            ot_room="OT-01",
            procedure_name="Synthetic demonstration procedure",
            status="scheduled",
            scheduled_at=datetime.now(UTC),
        )
        camera = OTDevice(device_code="SIM-CAM-01", device_type="camera", display_name="Simulated OT Camera", state="standby")
        db.add_all([session, camera])
        db.flush()
        db.add_all([
            VitalSign(surgical_session=session, heart_rate=72, spo2=98, blood_pressure="118/76", respiratory_rate=16, temperature_c=36.8),
            Alert(surgical_session=session, severity="info", message="Synthetic session scheduled; no clinical workflow is active."),
            RobotStatus(surgical_session=session, mode="standby", connected=False, details={"note": "simulation only"}),
            DeviceCommand(user=technician, device=camera, command_name="simulation_status_check", payload={"simulation": True}),
            AIInteraction(user=surgeon, interaction_type="demo", prompt_summary="Synthetic demo interaction", response_summary="No AI functionality is implemented."),
            AuditLog(user=admin, action="seed_database", entity_type="system", details={"synthetic": True}),
        ])
        db.commit()
    print("Synthetic AI-OT seed data created.")


if __name__ == "__main__":
    seed_database()
