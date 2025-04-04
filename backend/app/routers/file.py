from fastapi import APIRouter, HTTPException
from typing import List, Dict
from ..services.file_service import FileService
from ..core.config import config_manager

router = APIRouter(prefix="/files", tags=["files"])
file_service = FileService(config_manager)

@router.get("/extensions")
async def get_supported_extensions() -> List[str]:
    """Get list of supported media file extensions"""
    return file_service.get_supported_extensions()

@router.get("/libraries")
async def get_media_libraries() -> List[Dict]:
    """Get list of configured media libraries"""
    libraries = file_service.get_media_libraries()
    return [library.dict() for library in libraries]

@router.get("/scan")
async def scan_directory(directory: str) -> List[Dict]:
    """Scan a directory for media files"""
    try:
        return await file_service.scan_directory(directory)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 