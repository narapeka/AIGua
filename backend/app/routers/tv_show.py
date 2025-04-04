from fastapi import APIRouter, HTTPException
from typing import List, Dict
from ..services.tv_show_service import TVShowService
from ..core.config import config_manager

router = APIRouter(prefix="/tv", tags=["tv"])
tv_service = TVShowService(config_manager)

@router.get("/scan")
async def scan_tv_shows(directory: str) -> List[Dict]:
    """Scan a directory for TV show files"""
    try:
        return await tv_service.scan_directory(directory)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/identify")
async def identify_tv_show(file_path: str) -> Dict:
    """Identify a TV show file using TMDB"""
    try:
        result = await tv_service.identify_media(file_path)
        if not result:
            raise HTTPException(status_code=404, detail="TV show not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 