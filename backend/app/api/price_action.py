from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.ai_price_action.service import price_action_service

router = APIRouter()

@router.post("/fetch-data")
def trigger_data_ingestion(background_tasks: BackgroundTasks):
    """
    Triggers the AI #1 Fetcher to download and process market data.
    Runs in background to avoid freezing the dashboard.
    """
    try:
        background_tasks.add_task(price_action_service.fetch_all_data)
        return {"status": "started", "message": "Data ingestion started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train/{ticker}")
def train_model(ticker: str, background_tasks: BackgroundTasks):
    """
    Trains the Price Action LSTM Model for a specific ticker.
    Runs in background.
    """
    try:
        background_tasks.add_task(price_action_service.train_model, ticker)
        return {"status": "started", "message": f"Training for {ticker} started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predict/{ticker}")
def get_prediction(ticker: str):
    """
    Returns the AI's prediction for the next candle based on recent data.
    """
    try:
        result = price_action_service.predict(ticker)
        return result
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
