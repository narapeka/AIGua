from typing import List, Dict, Optional, Union
import tmdbsimple as tmdb
from ..core.config import config_manager
from ..core.rlimit import RateLimiter
from ..models.config import TMDBConfig
from ..models.settings import Settings
import os
import time
import logging

class TMDBService:
    """Centralized service for all TMDB operations using tmdbsimple"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.settings: Settings = config_manager.settings
        self.tmdb_config: TMDBConfig = self.settings.tmdb_config
        
        # Initialize TMDB API
        tmdb.API_KEY = self.tmdb_config.api_key
        self.language = self.tmdb_config.language
        
        # Initialize API objects
        self.search = tmdb.Search()
        self.movies = tmdb.Movies()
        self.tv = tmdb.TV()
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(self.tmdb_config.rate_limit)
        self.logger = logging.getLogger("tmdb_service")
    
    async def _make_request(self, func, *args, **kwargs):
        """Make a rate-limited API request with exponential backoff"""
        try:
            return await self.rate_limiter.execute_with_backoff(
                func,
                max_retries=3,
                base_delay=1.0,
                *args,
                **kwargs
            )
        except Exception as e:
            self.logger.error(f"TMDB API error: {str(e)}")
            raise
    
    async def search_movie(self, query: str) -> List[Dict]:
        """Search for a movie using TMDB API"""
        try:
            response = await self._make_request(
                self.search.movie,
                query=query,
                language=self.language
            )
            return response.get("results", [])
        except Exception as e:
            self.logger.error(f"Movie search failed: {str(e)}")
            return []
    
    async def search_tv_show(self, query: str) -> List[Dict]:
        """Search for a TV show using TMDB API"""
        try:
            response = await self._make_request(
                self.search.tv,
                query=query,
                language=self.language
            )
            return response.get("results", [])
        except Exception as e:
            self.logger.error(f"TV show search failed: {str(e)}")
            return []
    
    async def get_movie(self, movie_id: str) -> Optional[Dict]:
        """Get movie details"""
        try:
            return await self._make_request(
                self.movies(movie_id).info,
                language=self.language,
                append_to_response="credits,external_ids"
            )
        except Exception as e:
            self.logger.error(f"Failed to get movie details: {str(e)}")
            return None
    
    async def get_tv_show(self, tv_id: str) -> Optional[Dict]:
        """Get TV show details"""
        try:
            return await self._make_request(
                self.tv(tv_id).info,
                language=self.language,
                append_to_response="credits,external_ids"
            )
        except Exception as e:
            self.logger.error(f"Failed to get TV show details: {str(e)}")
            return None
    
    async def get_tv_season(self, show_id: str, season_number: int) -> Optional[Dict]:
        """Get TV season details"""
        try:
            return self.tv(show_id).season(season_number).info(
                language=self.language
            )
        except Exception:
            return None
    
    async def get_tv_episode(self, show_id: str, season_number: int, episode_number: int) -> Optional[Dict]:
        """Get TV episode details"""
        try:
            return self.tv(show_id).season(season_number).episode(episode_number).info(
                language=self.language
            )
        except Exception:
            return None
    
    def get_image_url(self, path: str, size: str = "w500") -> str:
        """Get full image URL for a given path and size"""
        return f"https://image.tmdb.org/t/p/{size}{path}"
    
    def get_poster_url(self, poster_path: Optional[str], size: str = "w500") -> Optional[str]:
        """Get full poster URL"""
        return self.get_image_url(poster_path, size) if poster_path else None
    
    def get_backdrop_url(self, backdrop_path: Optional[str], size: str = "w1280") -> Optional[str]:
        """Get full backdrop URL"""
        return self.get_image_url(backdrop_path, size) if backdrop_path else None
    
    def get_profile_url(self, profile_path: Optional[str], size: str = "w185") -> Optional[str]:
        """Get full profile URL"""
        return self.get_image_url(profile_path, size) if profile_path else None
    
    async def identify_media_from_name(self, name: str, media_type: str = "auto") -> Optional[Dict]:
        """
        Identify media from a name using TMDB API
        Args:
            name: The name to search for
            media_type: Type of media to search for ("movie", "tv", or "auto")
        Returns:
            Dict containing the identified media information or None if not found
        """
        cleaned_name = self._clean_name(name)
        
        if media_type == "auto":
            # Try both movie and TV show search
            movie_results = await self.search_movie(cleaned_name)
            tv_results = await self.search_tv_show(cleaned_name)
            
            # Combine and sort results by popularity
            all_results = []
            for result in movie_results:
                result["media_type"] = "movie"
                all_results.append(result)
            for result in tv_results:
                result["media_type"] = "tv"
                all_results.append(result)
            
            all_results.sort(key=lambda x: x.get("popularity", 0), reverse=True)
            return all_results[0] if all_results else None
        
        elif media_type == "movie":
            results = await self.search_movie(cleaned_name)
            if results:
                results[0]["media_type"] = "movie"
                return results[0]
        
        elif media_type == "tv":
            results = await self.search_tv_show(cleaned_name)
            if results:
                results[0]["media_type"] = "tv"
                return results[0]
        
        return None
    
    def _clean_name(self, name: str) -> str:
        """
        Clean a name for searching
        Removes common patterns that might interfere with search
        """
        # Remove year in parentheses
        name = name.split("(")[0].strip()
        
        # Remove quality indicators
        quality_indicators = ["1080p", "720p", "2160p", "4K", "HDR", "BluRay", "WEB-DL", "BRRip"]
        for indicator in quality_indicators:
            name = name.replace(indicator, "").strip()
        
        # Remove common separators
        separators = ["-", "_", "."]
        for separator in separators:
            name = name.replace(separator, " ").strip()
        
        return name
    
    @staticmethod
    def clean_name(name: str) -> str:
        """Static method to clean a name"""
        return TMDBService._clean_name(name)
    
    def _clean_name(self, name: str) -> str:
        """Clean a name for TMDB search"""
        import re
        # Remove year, quality, resolution, etc.
        clean_name = re.sub(r'\([0-9]{4}\)|\[.*?\]|\(.*?\)|1080p|720p|2160p|4K|HDR|BluRay|WEB-DL|BRRip|HDRip|DVDRip', '', name)
        # Remove file extension
        clean_name = os.path.splitext(clean_name)[0]
        # Remove extra spaces
        clean_name = ' '.join(clean_name.split())
        return clean_name.strip() 