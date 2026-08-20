from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    patient_id: int | None = None


class AIChatResponse(BaseModel):
    answer: str
    patient_id: int | None = None
    disclaimer: str = "AI responses are for informational assistance only and are not a substitute for professional clinical judgment."
