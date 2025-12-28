from fastapi import APIRouter, HTTPException
from app.services.ai_chart_vision.service import chart_vision_service
from typing import Optional

router = APIRouter()

@router.post("/load/{ticker}")
def load_ticker_visuals(ticker: str):
    """
    Preloads the visualization engine with ticker data.
    """
    result = chart_vision_service.load_data(ticker)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/render/{ticker}")
def get_chart_state(ticker: str, timeframe: str = "4H", hover_index: Optional[int] = None):
    """
    Returns the render state (JSON) for the frontend canvas.
    Supports 'hover_index' for Time-Travel/Ghost logic.
    """
    return chart_vision_service.get_chart_data(ticker, timeframe, hover_index)
