from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import config_manager
from .routers import config, media, tmdb

app = FastAPI(title="AIGua API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with clear organization
# 1. Configuration endpoints
app.include_router(config.router, prefix="/api/config", tags=["config"])

# 2. Media-related endpoints (files, movies, TV shows)
app.include_router(media.router, prefix="/api/media", tags=["media"])

# 3. External API endpoints (TMDB)
app.include_router(tmdb.router, prefix="/api/tmdb", tags=["tmdb"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Load settings
    settings = config_manager.load_settings()
    
    # Initialize services with config
    # Services will be initialized when needed by the routers
    
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # Close any open connections
    pass

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to AIGua API"}

@app.get("/test")
async def test():
    return {"message": "Test endpoint working"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"} 