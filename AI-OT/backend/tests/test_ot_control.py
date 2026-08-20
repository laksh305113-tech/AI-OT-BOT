import unittest

from app.services.ot_control_service import get_ot_devices, process_ot_device_command, set_emergency_stop


class OTControlTests(unittest.TestCase):
    def test_get_ot_devices_contains_simulated_devices(self):
        items = get_ot_devices()
        self.assertTrue(any(device["device_type"] == "surgical_light" for device in items))
        self.assertTrue(any(device["device_type"] == "camera" for device in items))
        self.assertTrue(any(device["device_type"] == "display" for device in items))
        self.assertTrue(any(device["device_type"] == "operating_table" for device in items))

    def test_valid_command_updates_simulated_device_state(self):
        result = process_ot_device_command(
            device_selector="ot_light_1",
            command_name="intensity",
            payload={"intensity": 80},
            user_role="surgeon",
            user_id=1,
            db=None,
        )
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["state"]["intensity"], 80)

    def test_invalid_value_is_rejected(self):
        result = process_ot_device_command(
            device_selector="ot_light_1",
            command_name="intensity",
            payload={"intensity": 140},
            user_role="surgeon",
            user_id=1,
            db=None,
        )
        self.assertEqual(result["status"], "invalid")

    def test_emergency_stop_disables_all_commands(self):
        set_emergency_stop(True)
        try:
            result = process_ot_device_command(
                device_selector="camera_1",
                command_name="zoom",
                payload={"zoom": 2},
                user_role="ot_technician",
                user_id=1,
                db=None,
            )
            self.assertEqual(result["status"], "emergency_stop")
        finally:
            set_emergency_stop(False)


if __name__ == "__main__":
    unittest.main()
