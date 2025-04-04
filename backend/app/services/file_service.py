from typing import List, Dict, Optional
import os
from ..core.config import config_manager
from ..models.config import MediaConfig, MediaLibrary
from ..services.movie_service import MovieService
from ..services.tv_show_service import TVShowService

class FileService:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.media_config: MediaConfig = config_manager.settings.media_config
        self.movie_service = MovieService(config_manager)
        self.tv_service = TVShowService(config_manager)

    def get_supported_extensions(self) -> List[str]:
        """Get list of supported media file extensions"""
        return self.media_config.supported_extensions

    def is_supported_file(self, filename: str) -> bool:
        """Check if a file has a supported extension"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.media_config.supported_extensions

    def get_media_libraries(self) -> List[Dict]:
        """Get list of configured media libraries"""
        return self.media_config.libraries

    async def scan_directory(self, directory: str) -> List[Dict]:
        """Scan a directory for media files"""
        results = []
        
        # First, try to identify if this is a movie or TV show directory
        # by checking the directory name and structure
        if self._is_movie_directory(directory):
            # Use movie service to scan
            movies = await self.movie_service.scan_directory(directory)
            for movie in movies:
                results.append(movie.dict())
        elif self._is_tv_show_directory(directory):
            # Use TV show service to scan
            tv_show = await self.tv_service.scan_directory(directory)
            results.append(tv_show.dict())
        else:
            # Generic scan for any media files
            for root, _, files in os.walk(directory):
                for file in files:
                    if self.is_supported_file(file):
                        file_path = os.path.join(root, file)
                        results.append({
                            "path": file_path,
                            "name": file,
                            "size": os.path.getsize(file_path),
                            "modified": os.path.getmtime(file_path)
                        })
        
        return results
    
    def _is_movie_directory(self, directory: str) -> bool:
        """Check if a directory is likely a movie directory"""
        # Check if directory name matches movie naming pattern
        dir_name = os.path.basename(directory)
        # Simple check - could be enhanced with more sophisticated patterns
        return "(" in dir_name and ")" in dir_name and any(
            dir_name.lower().endswith(ext.lower()) for ext in self.media_config.movie_extensions
        )
    
    def _is_tv_show_directory(self, directory: str) -> bool:
        """Check if a directory is likely a TV show directory"""
        # Check for season subdirectories
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                # Check if directory name contains "season" or "s" followed by numbers
                if "season" in item.lower() or (item.lower().startswith("s") and any(c.isdigit() for c in item)):
                    return True
        return False

    def get_library_for_path(self, file_path: str) -> Optional[Dict]:
        """Get the media library configuration for a given file path"""
        for library in self.media_config.libraries:
            if file_path.startswith(library.path):
                return library.dict()
        return None 