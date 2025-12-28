# tryouts

Run and test instructions for this repository.

Backend (Python / FastAPI)

- Create a virtual environment and install base deps:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
pip install -r backend/requirements-base.txt
```

- Optional heavy ML deps (local/dev only):

```bash
pip install -r backend/requirements-ml.txt
```

- Run the backend (from repo root):

```bash
PYTHONPATH=backend uvicorn app.main:app --reload --port 8000
```

- Run unit tests:

```bash
cd backend
pytest -q
```

Frontend (Vite / React)

- Install and run dev server:

```bash
cd frontend
npm ci
npm run dev
```

- E2E tests (Playwright):

```bash
cd frontend
npx playwright install
npx playwright test
```

CI notes

- GitHub Actions workflow splits base dependencies and optional ML deps. E2E runs in a separate job.
# Unified Strategic Engine

## Overview
A Local Web Application integrating multiple AI agents for trading strategy analysis and execution.
- **Backend**: FastAPI (Python)
- **Frontend**: React (Vite)
- **Database**: SQLite
- **AI #2**: Strategy Interpretation & Logic Compiler (located in `backend/app/services/ai_strategy_engine`)

## Setup Instructions

### Backend
1. Navigate to `backend/`
2. Install dependencies: `pip install -r requirements.txt`
3. Run Server: `python app/main.py`
   - API will be at `http://localhost:8000`
   - Docs at `http://localhost:8000/docs`

### Frontend
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Run Dev Server: `npm run dev`
   - UI will be at `http://localhost:5173`
   - To point the UI to a custom backend, set a Vite env var in `frontend/.env` or `frontend/.env.development`:
     - `VITE_API_BASE_URL=http://localhost:8000/api/v1` (default fallback is `http://localhost:8000/api/v1`)

## Directory Structure
```
root/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── db/
│   │   └── services/
│   │       └── ai_strategy_engine/  <-- AI #2 Logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
└── data/
    └── strategic_engine.db
```
