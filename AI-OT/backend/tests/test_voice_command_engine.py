import unittest

from app.services.command_engine import detect_command_intent, validate_and_approve_command


class VoiceCommandEngineTests(unittest.TestCase):
    def test_show_patient_history(self):
        command = detect_command_intent("Show patient history.")
        self.assertEqual(command["intent"], "PATIENT_HISTORY")
        self.assertEqual(command["device"], "patient_record")

    def test_show_latest_xray(self):
        command = detect_command_intent("Show latest X-ray.")
        self.assertEqual(command["intent"], "LATEST_IMAGING")
        self.assertEqual(command["device"], "imaging_xray")

    def test_start_monitoring(self):
        command = detect_command_intent("Start monitoring.")
        self.assertEqual(command["intent"], "START_MONITORING")
        self.assertEqual(command["device"], "monitoring")

    def test_show_camera_2(self):
        command = detect_command_intent("Show camera 2.")
        self.assertEqual(command["intent"], "SHOW_CAMERA")
        self.assertEqual(command["device"], "camera_2")

    def test_zoom_camera_2_to_2x(self):
        command = detect_command_intent("Zoom camera 2 to 2x.")
        self.assertEqual(command["intent"], "CAMERA_ZOOM")
        self.assertEqual(command["device"], "camera_2")
        self.assertEqual(command["value"], 2)

    def test_light_intensity_to_80_percent(self):
        command = detect_command_intent("Increase OT light intensity to 80 percent.")
        self.assertEqual(command["intent"], "LIGHT_INTENSITY")
        self.assertEqual(command["device"], "ot_light_1")
        self.assertEqual(command["value"], 80)

    def test_validate_and_approve_valid_surgeon_commands(self):
        command = {"intent": "LIGHT_INTENSITY", "device": "ot_light_1", "value": 80}
        result = validate_and_approve_command(command, "surgeon", user_id=1, db=None)
        self.assertEqual(result["status"], "approved")
        self.assertTrue(result["simulated_result"]["executed"])

    def test_reject_unauthorized_command(self):
        command = {"intent": "CAMERA_ZOOM", "device": "camera_2", "value": 2}
        result = validate_and_approve_command(command, "admin", user_id=1, db=None)
        self.assertEqual(result["status"], "rejected")

    def test_reject_invalid_value(self):
        command = {"intent": "LIGHT_INTENSITY", "device": "ot_light_1", "value": 150}
        result = validate_and_approve_command(command, "surgeon", user_id=1, db=None)
        self.assertEqual(result["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
