from fastapi import APIRouter, HTTPException
from app.services.ai_pattern_discovery.service import pattern_discovery_service

router = APIRouter()

@router.post("/run/{ticker}")
def run_discovery_cycle(ticker: str):
    """
    Triggers the Pattern Discovery AI (Mining, Masking, Curiosity) on a specific ticker.
    """
    result = pattern_discovery_service.run_discovery(ticker)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/patterns")
def get_discovered_patterns():
    """
    Returns the persistent memory of patterns discovered so far.
    """
    return pattern_discovery_service.get_patterns()
