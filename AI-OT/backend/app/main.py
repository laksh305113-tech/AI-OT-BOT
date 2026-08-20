from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.database.session import engine
from app.schemas.health import DatabaseHealthResponse, HealthResponse
from app.api.ai import router as ai_router
from app.api.auth import router as auth_router
from app.api.patients import router as patients_router
from app.api.protected import router as protected_router
from app.api.ot_control import router as ot_control_router
from app.api.sessions import router as sessions_router
from app.api.voice import router as voice_router
from app.services.monitoring_service import monitoring_stream
from app.services.session_management_service import get_live_timeline

app = FastAPI(title=get_settings().project_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(ai_router)
app.include_router(voice_router)
app.include_router(ot_control_router)
app.include_router(sessions_router)
app.include_router(protected_router)


@app.get("/api/health")
async def health_check() -> HealthResponse:
    """Return the availability of this prototype backend."""
    return HealthResponse(status="healthy", system=get_settings().project_name)


@app.websocket("/ws/monitoring/{session_id}")
async def monitoring_socket(websocket: WebSocket, session_id: str) -> None:
    await monitoring_stream.connect(session_id, websocket)
    try:
        await monitoring_stream.stream(session_id, websocket)
    except WebSocketDisconnect:
        monitoring_stream.disconnect(session_id, websocket)


@app.websocket("/ws/sessions/{session_id}")
async def session_timeline_socket(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    try:
        while True:
            payload = {
                "session_id": session_id,
                "timeline": get_live_timeline(int(session_id)) if session_id.isdigit() else [],
            }
            await websocket.send_json(payload)
            await __import__('asyncio').sleep(2)
    except WebSocketDisconnect:
        pass


@app.get("/api/health/database", response_model=DatabaseHealthResponse)
async def database_health_check() -> DatabaseHealthResponse:
    """Verify that PostgreSQL is reachable; it does not modify the database."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from error
    return DatabaseHealthResponse(status="healthy", database="postgresql")
