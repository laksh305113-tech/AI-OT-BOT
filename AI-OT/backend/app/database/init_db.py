"""Schema creation utility for the prototype database."""
from app.database.base import Base
from app.database.session import engine
import app.models.entities  # noqa: F401 - registers all models with Base metadata


def initialize_database() -> None:
    if str(engine.url).startswith("sqlite"):
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    initialize_database()
    print("AI-OT database tables created.")
