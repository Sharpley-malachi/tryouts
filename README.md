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
