from pydantic import BaseModel
from typing import Optional

class BasicConfig(BaseModel):
    """Basic application configuration"""
    proxy_url: Optional[str] = None
    debug_mode: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def get_default_config(cls) -> "BasicConfig":
        """Get default basic configuration"""
        return cls(
            proxy_url="",
            debug_mode=False,
            log_level="INFO"
        ) 