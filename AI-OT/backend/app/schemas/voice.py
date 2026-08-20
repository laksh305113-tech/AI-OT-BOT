from pydantic import BaseModel, Field


class VoiceCommandRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class VoiceCommandResponse(BaseModel):
    status: str
    intent: str
    device: str
    value: int | None = None
    reason: str | None = None
    simulated_result: dict | None = None
