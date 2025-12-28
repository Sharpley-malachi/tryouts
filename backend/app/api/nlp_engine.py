from fastapi import APIRouter, HTTPException
from app.services.ai_nlp.service import nlp_service

router = APIRouter()

@router.get("/generate-ebook/{market_type}")
def generate_ebook(market_type: str):
    """
    Generates a full educational eBook based on discovered patterns.
    market_type: 'FOREX' or 'INDICES'
    """
    try:
        book = nlp_service.generate_discovery_ebook(market_type)
        return book
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
