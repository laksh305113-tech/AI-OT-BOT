from __future__ import annotations

import asyncio
import math
import random
from collections.abc import AsyncIterator
from typing import Any

from fastapi import WebSocket


class MonitoringStream:
    def __init__(self) -> None:
        self._clients: dict[str, set[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.setdefault(session_id, set()).add(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        self._clients.get(session_id, set()).discard(websocket)

    async def stream(self, session_id: str, websocket: WebSocket) -> None:
        try:
            while True:
                payload = self._build_payload(session_id)
                await websocket.send_json(payload)
                await asyncio.sleep(1.5)
        except Exception:
            pass

    def _build_payload(self, session_id: str) -> dict[str, Any]:
        t = asyncio.get_running_loop().time() if False else 0
        time_index = len(self._clients.get(session_id, set()))
        base_hr = 72 + math.sin(time_index / 3.0) * 6
        base_spo2 = 98 + math.sin(time_index / 5.0) * 1.5
        base_bp_sys = 118 + math.sin(time_index / 4.0) * 8
        base_bp_dia = 76 + math.cos(time_index / 4.5) * 6
        base_rr = 16 + math.sin(time_index / 6.0) * 2.5
        base_temp = 36.8 + math.sin(time_index / 7.0) * 0.5
        etco2 = 38 + math.sin(time_index / 2.7) * 4
        ecg_wave = [
            0.0,
            0.24,
            0.64,
            0.9,
            0.78,
            0.42,
            0.1,
            0.3,
            0.75,
            0.95,
            0.8,
            0.4,
            0.15,
            0.0,
        ]

        hr = round(max(50, min(120, base_hr + random.uniform(-3.0, 3.0))), 1)
        spo2 = round(max(90, min(100, base_spo2 + random.uniform(-1.5, 1.5))), 1)
        bp_sys = round(max(90, min(150, base_bp_sys + random.uniform(-5.0, 5.0))), 1)
        bp_dia = round(max(60, min(95, base_bp_dia + random.uniform(-4.0, 4.0))), 1)
        rr = round(max(10, min(30, base_rr + random.uniform(-2.0, 2.0))), 1)
        temp = round(max(35.5, min(38.5, base_temp + random.uniform(-0.3, 0.3))), 1)
        etco2_val = round(max(25, min(55, etco2 + random.uniform(-2.0, 2.0))), 1)

        alerts = []
        if spo2 < 93:
            alerts.append({"type": "SpO2 warning", "severity": "warning", "message": "SIMULATED ALERT: oxygen saturation low.", "value": spo2})
        if hr > 110 or hr < 55:
            alerts.append({"type": "Heart rate warning", "severity": "warning", "message": "SIMULATED ALERT: heart rate outside expected range.", "value": hr})
        if bp_sys > 140 or bp_dia > 90:
            alerts.append({"type": "Blood pressure warning", "severity": "warning", "message": "SIMULATED ALERT: blood pressure elevated.", "value": f"{bp_sys}/{bp_dia}"})
        if rr > 22 or rr < 12:
            alerts.append({"type": "Respiratory rate warning", "severity": "warning", "message": "SIMULATED ALERT: respiratory rate outside expected range.", "value": rr})

        return {
            "session_id": session_id,
            "status": "Monitoring Active",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat() + 'Z',
            "vitals": {
                "heart_rate": {"value": hr, "unit": "bpm"},
                "spo2": {"value": spo2, "unit": "%"},
                "blood_pressure": {"value": f"{bp_sys}/{bp_dia}", "unit": "mmHg"},
                "respiratory_rate": {"value": rr, "unit": "/min"},
                "temperature": {"value": temp, "unit": "°C"},
                "etco2": {"value": etco2_val, "unit": "mmHg"},
            },
            "waveform": {"ecg": ecg_wave},
            "alerts": alerts,
            "patient_status": "Stable",
            "history": [],
        }


monitoring_stream = MonitoringStream()
