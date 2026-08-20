import unittest

from app.services.session_management_service import create_session, end_session, get_session_events, pause_session, resume_session


class SessionManagementTests(unittest.TestCase):
    def test_create_session_and_list_timeline(self):
        session = create_session(
            patient_id=1,
            surgeon="Dr. Sam",
            procedure="Appendectomy",
            ot_number="OT-02",
            status="active",
        )
        self.assertEqual(session["status"], "active")
        self.assertTrue(session["session_id"])
        events = get_session_events(session["id"])
        self.assertTrue(events)

    def test_pause_and_resume_session(self):
        session = create_session(
            patient_id=1,
            surgeon="Dr. Sam",
            procedure="Appendectomy",
            ot_number="OT-02",
            status="active",
        )
        paused = pause_session(session["id"])
        self.assertEqual(paused["status"], "paused")
        resumed = resume_session(session["id"])
        self.assertEqual(resumed["status"], "active")

    def test_end_session_marks_completion(self):
        session = create_session(
            patient_id=1,
            surgeon="Dr. Sam",
            procedure="Appendectomy",
            ot_number="OT-02",
            status="active",
        )
        ended = end_session(session["id"])
        self.assertEqual(ended["status"], "completed")


if __name__ == "__main__":
    unittest.main()
