from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    system: str


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str
