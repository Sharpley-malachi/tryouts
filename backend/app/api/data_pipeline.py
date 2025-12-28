from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.services.ai_data_pipeline.service import pipeline_service
from typing import Dict, Any
import pandas as pd
import io

router = APIRouter()

@router.post("/ingest")
def ingest_data(payload: Dict[str, Any]):
    """
    Ingest manual CSV data payload (JSON).
    Expected structure: { "data": {"4H": [...], ...}, "metadata": {...} }
    """
    try:
        return pipeline_service.ingest_data(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest/csv")
async def ingest_csv(
    file: UploadFile = File(...),
    timeframe: str = Form(...)
):
    """
    Handle direct CSV upload from Frontend.
    Parses to JSON and routes to DataPipelineAgent.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Parse CSV to Dictionary
        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception as parse_error:
             raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(parse_error)}")

        # Convert to list of dicts (records)
        # Ensure column names are lower case for consistency if needed, but let's stick to raw
        records = df.to_dict(orient="records")
        
        # Construct the payload expected by the service
        # We guess the symbol from the filename if not provided
        symbol_guess = file.filename.split('.')[0] if file.filename else "UNKNOWN"
        
        payload = {
            "correlation_id": f"UPLOAD-{symbol_guess}",
            "data": {
                timeframe: records
            },
            "metadata": {
                "symbol": symbol_guess,
                "source": "manual_upload",
                "filename": file.filename,
                "timeframe": timeframe
            }
        }
        
        return pipeline_service.ingest_data(payload)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/prediction/snapshot")
def create_snapshot(payload: Dict[str, Any]):
    """
    Freeze state for a new prediction.
    """
    try:
        return {"prediction_id": pipeline_service.register_prediction(payload)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
def submit_feedback(payload: Dict[str, Any]):
    """
    Close the loop on a pending prediction.
    """
    try:
        return pipeline_service.submit_feedback(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
