"""Reset all synthetic demo-account passwords from DEMO_SEED_PASSWORD.

Only use this for the academic prototype. Passwords are re-hashed before being
stored; the plaintext environment value is never persisted in the database.
"""
from sqlalchemy import select

from app.auth.security import hash_password
from app.config import get_settings
from app.database.session import SessionLocal
from app.models.entities import User


def reset_demo_passwords() -> int:
    with SessionLocal() as db:
        users = db.scalars(select(User).where(User.email.like("%@aiot-demo.com"))).all()
        password_hash = hash_password(get_settings().demo_seed_password)
        for user in users:
            user.password_hash = password_hash
        db.commit()
        return len(users)


if __name__ == "__main__":
    updated = reset_demo_passwords()
    print(f"Updated {updated} synthetic demo account password hash(es).")
