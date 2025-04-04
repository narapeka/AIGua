from fastapi import APIRouter
from .file import router as file_router
from .tv_show import router as tv_router
from .movie import router as movie_router

# This is the media router that aggregates all media-related routers
router = APIRouter()

# Include routers with their specific prefixes
router.include_router(file_router)
router.include_router(tv_router)
router.include_router(movie_router) 