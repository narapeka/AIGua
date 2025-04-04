from pydantic import BaseModel
from typing import List, Optional, Dict
from .config import LLMConfig, TMDBConfig, MediaConfig, BasicConfig

class Settings(BaseModel):
    """Settings model for the application."""
    # LLM Settings
    llm_config: LLMConfig = LLMConfig.get_default_configs()["openai"]
    
    # TMDB Settings
    tmdb_config: TMDBConfig = TMDBConfig.get_default_config()
    
    # Media Library Settings
    media_config: MediaConfig = MediaConfig.get_default_config()
    
    # General Settings
    basic_config: BasicConfig = BasicConfig.get_default_config()
    
    # TMDB Settings
    tmdb_api_key: Optional[str] = None
    tmdb_rate_limit: Optional[int] = 50
    
    # Media Library Settings
    media_libraries: List[MediaLibrary] = []
    media_extension: Optional[str] = ".iso;.mkv;.mp4;.ts;.m2ts;.avi;.mov;.mpeg"
    subtitle_extension: Optional[str] = ".srt;.ass;.ssa"
    
    # Proxy Settings
    proxy_url: Optional[str] = None
    grok_batch_size: Optional[int] = 20 