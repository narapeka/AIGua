"""Files router aggregator that combines all file-related routers."""
from fastapi import APIRouter
from .file_scanner import router as scanner_router
from .file_identify import router as identify_router
from .file_renamer import router as renamer_router
from .tmdb_service import router as tmdb_router

# Create a combined router
router = APIRouter()

# Include all the individual routers - the prefix is already set in each router
router.include_router(scanner_router)
router.include_router(identify_router)
router.include_router(renamer_router)
router.include_router(tmdb_router) 