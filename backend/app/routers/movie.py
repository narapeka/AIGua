from fastapi import APIRouter, HTTPException
from typing import List, Dict
from ..services.movie_service import MovieService
from ..core.config import config_manager

router = APIRouter(prefix="/movies", tags=["movies"])
movie_service = MovieService(config_manager)

@router.get("/scan")
async def scan_movies(directory: str) -> List[Dict]:
    """Scan a directory for movie files"""
    try:
        return await movie_service.scan_directory(directory)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/identify")
async def identify_movie(file_path: str) -> Dict:
    """Identify a movie file using TMDB"""
    try:
        result = await movie_service.identify_media(file_path)
        if not result:
            raise HTTPException(status_code=404, detail="Movie not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 