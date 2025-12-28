from fastapi import APIRouter, HTTPException
from app.services.the_general.service import command_service
from pydantic import BaseModel
from app.services.ai_data_pipeline.service import pipeline_service

router = APIRouter()

class ModeRequest(BaseModel):
    mode: str

class HeartbeatRequest(BaseModel):
    agent_id: str
    confidence: float

@router.post("/mode")
def set_system_mode(req: ModeRequest):
    """
    Manually override the AI System Mode (INGESTION, RESEARCH, etc.)
    """
    return command_service.switch_mode(req.mode)

@router.post("/heartbeat")
def agent_heartbeat(req: HeartbeatRequest):
    """
    Endpoint for Agents to report their health/confidence.
    """
    return command_service.heartbeat(req.agent_id, req.confidence)

@router.get("/health")
def get_system_health():
    """
    Returns the High-Level Dashboard Metrics from The General.
    """
    return command_service.get_dashboard_metrics()

@router.post("/analyze")
def trigger_analysis(input: dict):
    """
    Trigger a general analysis (Placeholder/Proxy).
    """
    # Ideally this routes to a specific agent based on input
    return {"status": "analysis_started", "notes": "Route stub implementation"}

@router.post("/feedback")
def submit_feedback(payload: dict):
    """
    Accept feedback routed from the frontend and forward to the Data Pipeline for processing.
    Accepts either `prediction_id` or legacy `trade_id` field from the frontend and normalizes it.
    """
    try:
        # Normalize keys (frontend historically used `trade_id`)
        if 'prediction_id' not in payload and 'trade_id' in payload:
            payload['prediction_id'] = payload.pop('trade_id')

        if 'prediction_id' not in payload:
            raise HTTPException(status_code=400, detail="Missing prediction_id (or trade_id)")

        return pipeline_service.submit_feedback(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
