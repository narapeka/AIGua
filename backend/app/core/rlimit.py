"""Rate limiting utilities"""
import asyncio
import time
import logging
import random
from typing import Optional, Callable, Any

class RateLimiter:
    """Token bucket rate limiter with exponential backoff for API requests"""
    
    def __init__(self, rate: float, burst: Optional[float] = None):
        """
        Initialize rate limiter
        
        Args:
            rate: Number of tokens per second
            burst: Maximum number of tokens (defaults to rate)
        """
        self.rate = rate
        self.burst = burst if burst is not None else rate
        self.tokens = self.burst
        self.last_update = time.time()
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger("rate_limiter")
    
    async def wait_for_token(self) -> None:
        """Wait until a token is available"""
        async with self.lock:
            while self.tokens <= 0:
                now = time.time()
                time_passed = now - self.last_update
                self.tokens = min(
                    self.burst,
                    self.tokens + time_passed * self.rate
                )
                self.last_update = now
                
                if self.tokens <= 0:
                    wait_time = (1 - self.tokens) / self.rate
                    self.logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
            
            self.tokens -= 1
    
    async def execute_with_backoff(
        self,
        func: Callable[..., Any],
        max_retries: int = 3,
        base_delay: float = 1.0,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with exponential backoff retry logic
        
        Args:
            func: Function to execute
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                await self.wait_for_token()
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt == max_retries:
                    break
                
                # Calculate delay with exponential backoff and jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1 * base_delay)
                self.logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}. "
                    f"Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)
        
        raise last_exception 