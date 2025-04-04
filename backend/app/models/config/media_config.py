from pydantic import BaseModel, Field
from typing import List, Optional

class MediaLibrary(BaseModel):
    """Media library configuration"""
    path: str = Field(..., description="Path to the media library")
    type: str = Field(..., description="Type of media (movie or tv)")

class MediaConfig(BaseModel):
    """Configuration for media libraries"""
    libraries: List[MediaLibrary] = Field(default_factory=list, description="List of media libraries")
    media_extension: str = Field(
        default=".iso;.mkv;.mp4;.ts;.m2ts;.avi;.mov;.mpeg",
        description="Supported media file extensions, semicolon-separated"
    )
    subtitle_extension: str = Field(
        default=".srt;.ass;.ssa",
        description="Supported subtitle file extensions, semicolon-separated"
    )
    
    @classmethod
    def get_default_config(cls) -> "MediaConfig":
        """Get default media configuration"""
        return cls(
            libraries=[],
            media_extension=".iso;.mkv;.mp4;.ts;.m2ts;.avi;.mov;.mpeg",
            subtitle_extension=".srt;.ass;.ssa"
        ) 