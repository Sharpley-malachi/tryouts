from fastapi import APIRouter, HTTPException
from app.services.ai_document_generator.service import publishing_service

router = APIRouter()

@router.post("/publish/{wing}")
def trigger_publication(wing: str):
    """
    Triggers the creation/update of documents for a specific wing (FOREX/INDICES).
    """
    try:
        result = publishing_service.publish_wing(wing.upper())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/library")
def get_library_contents():
    """
    Returns the list of available documents in the AI #6 Library.
    """
    return publishing_service.get_library_index()
