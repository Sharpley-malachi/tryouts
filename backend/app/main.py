from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api import price_action
from app.api import pattern_discovery
from app.api import nlp_engine
from app.api import chart_vision
from app.api import document_generator
from app.api import the_general
from app.api import data_pipeline
from app.api.endpoints import temporal

app = FastAPI(title="Unified Strategic Engine", version="1.0.0")

# CORS Setup for React Frontend
origins = [
    "http://localhost",
    "http://localhost:5173", # Vite default port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(price_action.router, prefix="/api/v1/price-action", tags=["AI #1 Price Action"])
app.include_router(pattern_discovery.router, prefix="/api/v1/pattern-discovery", tags=["AI #3 Pattern Discovery"])
app.include_router(nlp_engine.router, prefix="/api/v1/nlp", tags=["AI #4 NLP Engine"])
app.include_router(chart_vision.router, prefix="/api/v1/chart-vision", tags=["AI #5 Chart Vision"])
app.include_router(document_generator.router, prefix="/api/v1/publishing", tags=["AI #6 Publishing House"])
app.include_router(the_general.router, prefix="/api/v1/general", tags=["AI #7 The General"])
app.include_router(data_pipeline.router, prefix="/api/v1/pipeline", tags=["AI #8 Data Pipeline"])
app.include_router(temporal.router, prefix="/api/v1/ledger", tags=["Truth Ledger & Verification"])

@app.get("/")
def read_root():
    return {"message": "Unified Strategic Engine Online"}

@app.get("/health")
def health_check():
    return {"status": "active", "db_status": "connected"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
