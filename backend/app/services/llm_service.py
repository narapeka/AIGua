"""Service for managing LLM operations using OpenAI SDK"""
import json
import logging
from typing import List, Dict, Optional, Any
import openai
from ..core.config import config_manager
from ..core.rlimit import RateLimiter
from ..models.config import LLMConfig
from ..models.settings import Settings

class LLMService:
    """Service for managing LLM operations using OpenAI SDK"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.settings: Settings = config_manager.settings
        self.llm_config: LLMConfig = self.settings.llm_config
        self.logger = logging.getLogger(f"llm.{self.llm_config.provider}")
        
        # Configure OpenAI client
        openai.api_key = self.llm_config.api_key
        openai.base_url = self.llm_config.base_url
        
        # Set proxy if configured
        if self.settings.general_config.proxy_url:
            openai.proxy = f"http://{self.settings.general_config.proxy_url}"
            
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(self.llm_config.rate_limit)
    
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
            self.logger.error(f"LLM API error: {str(e)}")
            raise
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available LLM providers"""
        return ["grok", "gemini", "openai", "deepseek"]
    
    @staticmethod
    def get_default_config(provider: str) -> LLMConfig:
        """Get default configuration for a specific provider"""
        return LLMConfig.get_default_configs()[provider]
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send a chat completion request using OpenAI SDK"""
        try:
            response = await self._make_request(
                openai.ChatCompletion.acreate,
                model=self.llm_config.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"LLM chat completion failed: {str(e)}")
            raise Exception(f"LLM chat completion failed: {str(e)}")
    
    async def parse_filenames(self, filenames: List[str], media_types: Dict[str, str] = None) -> List[Dict]:
        """Parse a list of filenames using LLM"""
        if not filenames:
            return []
            
        # Process in batches
        batch_size = self.llm_config.batch_size
        results = []
        
        for i in range(0, len(filenames), batch_size):
            batch = filenames[i:i + batch_size]
            batch_results = await self._parse_batch(batch, media_types)
            results.extend(batch_results)
            
        return results
    
    async def _parse_batch(self, filenames: List[str], media_types: Dict[str, str] = None) -> List[Dict]:
        """Parse a batch of filenames"""
        if media_types is None:
            media_types = {filename: "movie" for filename in filenames}
            
        # Determine batch type
        types = list(media_types.values())
        is_movie_batch = all(t == "movie" for t in types)
        is_tv_batch = all(t == "tv" for t in types)
        
        # Build prompt based on batch type
        if is_movie_batch:
            system_prompt = "You are a professional movie information parser. Parse movie filenames and return JSON with Chinese title, English title, and year. Return valid JSON only."
            user_prompt = "Parse these movie filenames and return JSON with Chinese title, English title, and year:\n\n"
        elif is_tv_batch:
            system_prompt = "You are a professional TV show information parser. Parse TV show filenames and return JSON with Chinese title, English title, and year. Return valid JSON only."
            user_prompt = "Parse these TV show filenames and return JSON with Chinese title, English title, and year:\n\n"
        else:
            system_prompt = "You are a professional media information parser. Parse filenames and return JSON with Chinese title, English title, and year. Return valid JSON only."
            user_prompt = "Parse these filenames and return JSON with Chinese title, English title, and year:\n\n"
            
        # Add filenames to prompt
        for i, filename in enumerate(filenames, 1):
            media_type = media_types.get(filename, "movie")
            media_type_text = "Movie" if media_type == "movie" else "TV Show"
            user_prompt += f"{i}. {filename} (Type: {media_type_text})\n"
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            content = await self.chat_completion(messages)
            return self._parse_llm_response(content, filenames)
        except Exception as e:
            self.logger.error(f"Error parsing filenames: {str(e)}")
            return [{"error": str(e)} for _ in filenames]
    
    def _parse_llm_response(self, content: str, filenames: List[str]) -> List[Dict]:
        """Parse LLM response into structured data"""
        try:
            # Extract JSON from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            if start_idx == -1 or end_idx == 0:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
                
            json_str = content[start_idx:end_idx]
            json_str = json_str.replace('\n', ' ').replace('\r', '')
            
            # Parse JSON
            results = json.loads(json_str)
            
            # Ensure results match input length
            if isinstance(results, list):
                if len(results) != len(filenames):
                    self.logger.warning(f"Result count mismatch: expected {len(filenames)}, got {len(results)}")
                    # Pad or truncate results
                    if len(results) < len(filenames):
                        results.extend([{"error": "Missing result"} for _ in range(len(filenames) - len(results))])
                    else:
                        results = results[:len(filenames)]
            else:
                # Single result case
                results = [results] * len(filenames)
                
            return results
            
        except Exception as e:
            self.logger.error(f"Error parsing LLM response: {str(e)}")
            return [{"error": f"Parse error: {str(e)}"} for _ in filenames]
    
    async def validate_connection(self) -> bool:
        """Test the connection to the LLM provider"""
        try:
            # Send a simple test message
            await self.chat_completion([
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Test connection"}
            ])
            return True
        except Exception:
            return False
    
    async def get_available_models(self) -> List[str]:
        """Get list of available models for the current provider"""
        return [self.llm_config.model]
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available LLM providers"""
        return list(LLMConfig.get_default_configs().keys())
    
    @classmethod
    def get_default_config(cls, provider: str) -> LLMConfig:
        """Get default configuration for a provider"""
        configs = LLMConfig.get_default_configs()
        if provider not in configs:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        return configs[provider] 