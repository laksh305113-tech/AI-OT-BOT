# AI-OT — AI Integrated Operating Theatre Assistance System

## Purpose

AI-OT is an academic prototype for an AI-powered Operating Theatre command center. This initial foundation provides a React frontend, a FastAPI backend, and placeholder directories for future work.

## Safety disclaimer

**This is not a clinically approved medical system.** It must use only synthetic or demo patient data. Medical devices, OT equipment, patient monitors, cameras, surgical robots, and all other clinical integrations are simulated only. Do not connect this prototype to, or use it to control, real medical equipment.

## Technology stack

- Frontend: React, Vite, JavaScript, HTML, CSS, React Router, Axios
- Backend: Python, FastAPI, Uvicorn
- Database: PostgreSQL, SQLAlchemy

## Project layout

```text
AI-OT/
├── frontend/                 # React/Vite application
├── backend/                  # FastAPI application
├── database/                 # Database resources placeholder
├── docs/                     # Documentation placeholder
└── tests/                    # Tests placeholder
```

## Frontend setup

```powershell
cd frontend
npm install
```

## Backend setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Database setup (PostgreSQL)

1. Copy `.env.example` to `.env` in the project root and replace every placeholder with your local PostgreSQL values. Do not commit `.env`.
2. Start PostgreSQL:

```powershell
docker compose --env-file .env up -d postgres
```

3. From the `backend` directory, create the schema and add synthetic seed data:

```powershell
python -m app.database.init_db
python -m app.database.seed
```

The seed command is idempotent and creates five synthetic users (admin, surgeon, anesthetist, nurse, OT technician), three synthetic patients, and example prototype records.

## Authentication

Set a unique `JWT_SECRET_KEY` and a local `DEMO_SEED_PASSWORD` in `.env` before seeding. The provided prototype template uses `123456` for the synthetic demo accounts; replace it outside a local academic demo. The seed process stores only Argon2 password hashes in PostgreSQL.

Login is available at `POST /api/auth/login` and accepts JSON:

```json
{
  "email": "surgeon@aiot-demo.com",
  "password": "the-value-of-DEMO_SEED_PASSWORD"
}
```

The React app redirects unauthenticated visitors to `/login`; successful login redirects to the dashboard. All backend prototype module endpoints require a Bearer token and independently enforce roles.

Synthetic seeded accounts are `admin@aiot-demo.com`, `surgeon@aiot-demo.com`, `anesthetist@aiot-demo.com`, `nurse@aiot-demo.com`, and `technician@aiot-demo.com`. They share the local password you set in `DEMO_SEED_PASSWORD`.

To update already-seeded synthetic accounts after changing `DEMO_SEED_PASSWORD`, run:

```powershell
python -m app.database.reset_demo_passwords
```

## Run the project

Run these commands in separate terminals.

Frontend:

```powershell
cd frontend
npm run dev
```

Open the URL printed by Vite, normally `http://localhost:5173`.

Backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000` by default.

## Health check

With the backend running, request:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

Expected response:

```json
{
  "status": "healthy",
  "system": "AI-OT"
}
```

Database connectivity can be checked after PostgreSQL is running:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health/database
```
