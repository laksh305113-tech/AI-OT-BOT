import unittest
from io import BytesIO

from fastapi.testclient import TestClient

from app.auth.security import create_access_token
from app.database.init_db import initialize_database
from app.database.session import SessionLocal
from app.main import app
from app.models.entities import Patient, User


class MedicalImagingTests(unittest.TestCase):
    def setUp(self):
        initialize_database()
        with SessionLocal() as db:
            db.query(User).delete()
            db.query(Patient).delete()
            user = User(
                email="imaging@aiot-demo.com",
                display_name="Dr. Imaging",
                role="surgeon",
                password_hash="unused",
            )
            patient = Patient(
                synthetic_identifier="SYN-IMG-001",
                display_name="Synthetic Imaging Patient",
                patient_id="IMG-001",
                name="Synthetic Imaging Patient",
                gender="female",
            )
            db.add_all([user, patient])
            db.commit()
            db.refresh(user)
            db.refresh(patient)
            self.user_id = user.id
            self.patient_id = patient.id
            self.token = create_access_token(user.id)

    def test_get_patient_images_empty(self):
        client = TestClient(app)
        response = client.get(
            f"/api/patients/{self.patient_id}/images",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_upload_patient_image(self):
        client = TestClient(app)
        image_bytes = b"fake-image-bytes" 
        response = client.post(
            f"/api/patients/{self.patient_id}/images",
            headers={"Authorization": f"Bearer {self.token}"},
            files={"file": ("scan.png", BytesIO(image_bytes), "image/png")},
            data={"modality": "XRAY", "description": "Chest X-ray prototype"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        payload = response.json()
        self.assertEqual(payload["modality"], "XRAY")
        self.assertEqual(payload["description"], "Chest X-ray prototype")
        self.assertEqual(payload["patient_id"], self.patient_id)


if __name__ == "__main__":
    unittest.main()
