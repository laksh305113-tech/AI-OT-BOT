import unittest

from fastapi.testclient import TestClient

from app.main import app


class MonitoringWebSocketTests(unittest.TestCase):
    def test_monitoring_socket_streams_data(self):
        client = TestClient(app)
        with client.websocket_connect('/ws/monitoring/session-01') as websocket:
            message = websocket.receive_json()
            self.assertIn('status', message)
            self.assertIn('vitals', message)
            self.assertIn('alerts', message)
            self.assertIn('session_id', message)


if __name__ == '__main__':
    unittest.main()
