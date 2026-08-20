import os
import unittest

from app.config import Settings


class SettingsConfigTests(unittest.TestCase):
    def test_placeholder_env_values_are_ignored(self):
        os.environ["DATABASE_URL"] = "<your_database_user>"
        os.environ["JWT_SECRET_KEY"] = "<generate-a-long-random-secret>"
        try:
            settings = Settings()
            self.assertTrue(settings.database_url.startswith("sqlite"))
            self.assertEqual(settings.jwt_secret_key, "local-dev-secret")
        finally:
            os.environ.pop("DATABASE_URL", None)
            os.environ.pop("JWT_SECRET_KEY", None)


if __name__ == "__main__":
    unittest.main()
