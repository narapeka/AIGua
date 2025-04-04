from pydantic import BaseModel, Field
from typing import Optional

class TMDBConfig(BaseModel):
    """Configuration for TMDB API"""
    api_key: str = Field(..., description="TMDB API key")
    rate_limit: int = Field(default=50, description="Rate limit in requests per second")
    language: str = Field(default="en-US", description="Language for API responses")
    
    @classmethod
    def get_default_config(cls) -> "TMDBConfig":
        """Get default TMDB configuration"""
        return cls(
            api_key="",
            rate_limit=50,
            language="en-US"
        ) 