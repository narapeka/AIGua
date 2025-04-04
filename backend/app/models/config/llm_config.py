from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class LLMConfig(BaseModel):
    """Configuration for LLM services"""
    provider: str = Field(..., description="LLM provider (grok, gemini, openai, deepseek, etc.)")
    model: str = Field(..., description="Model name to use")
    api_key: str = Field(..., description="API key for the LLM service")
    base_url: str = Field(..., description="Base URL for the API")
    rate_limit: int = Field(default=1, description="Rate limit in requests per second")
    batch_size: int = Field(default=20, description="Batch size for processing files")
    
    @classmethod
    def get_default_configs(cls) -> Dict[str, "LLMConfig"]:
        """Get default configurations for known providers"""
        return {
            "grok": cls(
                provider="grok",
                model="grok-2-latest",
                api_key="",
                base_url="https://api.x.ai/v1",
                rate_limit=1,
                batch_size=20
            ),
            "gemini": cls(
                provider="gemini",
                model="gemini-2.0-flash",
                api_key="",
                base_url="https://generativelanguage.googleapis.com/v1beta/openai",
                rate_limit=1,
                batch_size=20
            ),
            "openai": cls(
                provider="openai",
                model="gpt-4o",
                api_key="",
                base_url="https://api.openai.com/v1",
                rate_limit=3,
                batch_size=20
            ),
            "deepseek": cls(
                provider="deepseek",
                model="deepseek-chat",
                api_key="",
                base_url="https://api.deepseek.com/v1",
                rate_limit=1,
                batch_size=20
            )
        } 