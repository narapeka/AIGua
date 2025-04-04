from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from ..services.tmdb_service import TMDBService
from ..core.config import config_manager

router = APIRouter()
tmdb_service = TMDBService(config_manager)

@router.get("/search/movie")
async def search_movie(query: str) -> List[Dict]:
    """Search for movies using TMDB API"""
    try:
        return await tmdb_service.search_movie(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/tv")
async def search_tv_show(query: str) -> List[Dict]:
    """Search for TV shows using TMDB API"""
    try:
        return await tmdb_service.search_tv_show(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/movie/{movie_id}")
async def get_movie(movie_id: str) -> Dict:
    """Get movie details from TMDB"""
    try:
        movie = await tmdb_service.get_movie(movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return movie
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tv/{show_id}")
async def get_tv_show(show_id: str) -> Dict:
    """Get TV show details from TMDB"""
    try:
        show = await tmdb_service.get_tv_show(show_id)
        if not show:
            raise HTTPException(status_code=404, detail="TV show not found")
        return show
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tv/{show_id}/season/{season_number}")
async def get_tv_season(show_id: str, season_number: int) -> Dict:
    """Get TV show season details from TMDB"""
    try:
        season = await tmdb_service.get_tv_season(show_id, season_number)
        if not season:
            raise HTTPException(status_code=404, detail="Season not found")
        return season
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tv/{show_id}/season/{season_number}/episode/{episode_number}")
async def get_tv_episode(show_id: str, season_number: int, episode_number: int) -> Dict:
    """Get TV show episode details from TMDB"""
    try:
        episode = await tmdb_service.get_tv_episode(show_id, season_number, episode_number)
        if not episode:
            raise HTTPException(status_code=404, detail="Episode not found")
        return episode
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/identify")
async def identify_media(name: str, media_type: str = "auto") -> Dict:
    """Identify media from name using TMDB"""
    try:
        result = await tmdb_service.identify_media_from_name(name, media_type)
        if not result:
            raise HTTPException(status_code=404, detail="Media not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 