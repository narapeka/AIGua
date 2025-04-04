from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
from ..core.config import config_manager, settings
from ..models.settings import Settings
from ..models.config import LLMConfig, TMDBConfig, MediaConfig, BasicConfig, MediaLibrary
from ..services.llm_service import LLMService

router = APIRouter()

class ConfigUpdate(BaseModel):
    llm_config: Optional[LLMConfig] = None
    tmdb_config: Optional[TMDBConfig] = None
    media_config: Optional[MediaConfig] = None
    basic_config: Optional[BasicConfig] = None

@router.get("/", response_model=Settings)
async def get_config():
    """Get current configuration"""
    return settings

@router.post("/", response_model=Settings)
async def update_config(config: ConfigUpdate):
    """Update configuration"""
    try:
        # Update LLM config if provided
        if config.llm_config:
            settings.llm_config = config.llm_config
        
        # Update TMDB config if provided
        if config.tmdb_config:
            settings.tmdb_config = config.tmdb_config
            
        # Update media config if provided
        if config.media_config:
            settings.media_config = config.media_config
            
        # Update basic config if provided
        if config.basic_config:
            settings.basic_config = config.basic_config
            
        # Save the updated settings
        config_manager.save_settings(settings)
        
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/llm/providers")
async def get_llm_providers():
    """Get available LLM providers"""
    return {"providers": LLMService.get_available_providers()}

@router.get("/llm/provider/{provider}")
async def get_llm_provider_config(provider: str):
    """Get default configuration for a specific LLM provider"""
    try:
        return LLMService.get_default_config(provider)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/test-connection")
async def test_connection():
    """Test API connections"""
    try:
        # Test LLM connection
        llm_service = LLMService(config_manager)
        await llm_service.chat_completion([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Test connection"}
        ])
        
        # TODO: Test TMDB connection
        
        return {"message": "Connection test completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}") 