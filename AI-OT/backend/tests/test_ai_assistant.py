import unittest

from app.services.ai_assistant import build_patient_context, generate_local_reply


class AIAssistantTests(unittest.TestCase):
    def test_build_patient_context_handles_missing_fields_without_inventing_data(self):
        patient = {
            "patient_id": "P-1001",
            "name": "Jane Smith",
            "age": 42,
            "gender": "female",
            "blood_group": None,
            "allergies": None,
            "current_medications": None,
            "previous_surgeries": None,
            "planned_procedure": "Appendectomy",
            "assigned_surgeon": "Dr. Patel",
            "ot_number": "OT-04",
            "scheduled_date": "2026-08-21",
            "medical_conditions": None,
            "preoperative_notes": None,
        }

        context = build_patient_context(patient)

        self.assertIn("Jane Smith", context["summary"])
        self.assertIn("No information is available in the patient's records.", context["allergies"])
        self.assertIn("Appendectomy", context["planned_procedure"])

    def test_local_reply_returns_safe_no_information_message(self):
        patient = {
            "patient_id": "P-1002",
            "name": "John Doe",
            "age": 33,
            "gender": "male",
            "allergies": None,
            "current_medications": None,
            "previous_surgeries": None,
            "medical_conditions": None,
            "planned_procedure": None,
        }

        response = generate_local_reply("What allergies does this patient have?", patient)

        self.assertIn("No information is available in the patient's records.", response)


if __name__ == "__main__":
    unittest.main()
