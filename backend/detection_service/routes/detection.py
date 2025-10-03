from fastapi import APIRouter, HTTPException
from typing import List
from ..database import detections_collection
from ..models.detection import DetectionModel
from pymongo import DESCENDING

router = APIRouter()

@router.get("/detections/", response_model=List[DetectionModel], tags=["Detections"])
async def get_recent_detections(limit: int = 100):
    """
    Retorna uma lista das detecções mais recentes.
    """
    try:
        cursor = detections_collection.find({}, {'_id': 0}).sort("timestamp", DESCENDING).limit(limit)
        return list(cursor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))