from pydantic import BaseModel
from typing import List, Optional
import yaml
import os
from pathlib import Path
from ..models.settings import Settings
from ..models.config import LLMConfig, TMDBConfig, MediaConfig, BasicConfig

class MediaLibrary(BaseModel):
    path: str
    type: str  # 'movie' 或 'tv'

class ConfigManager:
    """Configuration manager for the application"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.settings: Optional[Settings] = None
    
    def load_settings(self) -> Settings:
        """Load settings from config file or create default settings"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config_data = json.load(f)
                self.settings = Settings(**config_data)
        else:
            self.settings = Settings(
                llm_config=LLMConfig.get_default_configs()["openai"],
                tmdb_config=TMDBConfig.get_default_config(),
                media_config=MediaConfig.get_default_config(),
                basic_config=BasicConfig.get_default_config()
            )
            self.save_settings(self.settings)
        return self.settings
    
    def save_settings(self, settings: Settings) -> None:
        """Save settings to config file"""
        with open(self.config_file, "w") as f:
            json.dump(settings.dict(), f, indent=2)
        self.settings = settings
    
    def get_settings(self) -> Settings:
        """Get current settings, loading them if necessary"""
        if not self.settings:
            self.settings = self.load_settings()
        return self.settings

# Create a global config manager instance
config_manager = ConfigManager()
settings = config_manager.get_settings() 