import time
import functools
import random
from typing import Callable, Any, Tuple, Optional
from utils.logger import logger


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 10.0,
    timeout: Optional[float] = None,
    retry_on_exception: Tuple[type, ...] = (Exception,),
    retry_on_result: Optional[Callable[[Any], bool]] = None
):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            total_time = 0.0
            
            for attempt in range(max_retries):
                try:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    total_time += elapsed
                    
                    if retry_on_result and retry_on_result(result):
                        raise ValueError(f"Result failed check on attempt {attempt + 1}")
                    
                    if attempt > 0:
                        logger.info(f"Retry succeeded after {attempt + 1} attempts",
                                  function=func.__name__, total_time_ms=total_time * 1000)
                    return result
                    
                except retry_on_exception as e:
                    elapsed = time.time() - start_time
                    total_time += elapsed
                    
                    if timeout and total_time >= timeout:
                        logger.error(f"Timeout reached after {total_time:.2f}s",
                                   function=func.__name__, exception=e)
                        raise
                    
                    if attempt < max_retries - 1:
                        jitter = random.uniform(0, delay * 0.5)
                        wait_time = min(delay + jitter, max_delay)
                        
                        logger.warning(f"Retry attempt {attempt + 1}/{max_retries} failed",
                                      function=func.__name__, 
                                      error=str(e),
                                      wait_time_ms=wait_time * 1000)
                        
                        time.sleep(wait_time)
                        delay = min(delay * backoff_factor, max_delay)
                    else:
                        logger.error(f"All {max_retries} retries failed",
                                   function=func.__name__, exception=e)
                        raise
            
            return None
        return wrapper
    return decorator


class RetryHandler:
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 10.0,
        timeout: Optional[float] = None
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.timeout = timeout
    
    def execute(
        self,
        func: Callable,
        *args,
        retry_on_exception: Tuple[type, ...] = (Exception,),
        retry_on_result: Optional[Callable[[Any], bool]] = None,
        **kwargs
    ) -> Any:
        delay = self.initial_delay
        total_time = 0.0
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                total_time += elapsed
                
                if retry_on_result and retry_on_result(result):
                    raise ValueError(f"Result failed check on attempt {attempt + 1}")
                
                if attempt > 0:
                    logger.info(f"Retry succeeded after {attempt + 1} attempts",
                              function=func.__name__, total_time_ms=total_time * 1000)
                return result
                
            except retry_on_exception as e:
                elapsed = time.time() - start_time
                total_time += elapsed
                
                if self.timeout and total_time >= self.timeout:
                    logger.error(f"Timeout reached after {total_time:.2f}s",
                               function=func.__name__, exception=e)
                    raise
                
                if attempt < self.max_retries - 1:
                    jitter = random.uniform(0, delay * 0.5)
                    wait_time = min(delay + jitter, self.max_delay)
                    
                    logger.warning(f"Retry attempt {attempt + 1}/{self.max_retries} failed",
                                  function=func.__name__,
                                  error=str(e),
                                  wait_time_ms=wait_time * 1000)
                    
                    time.sleep(wait_time)
                    delay = min(delay * self.backoff_factor, self.max_delay)
                else:
                    logger.error(f"All {self.max_retries} retries failed",
                               function=func.__name__, exception=e)
                    raise
        
        return None


retry_handler = RetryHandler(
    max_retries=3,
    initial_delay=1.0,
    backoff_factor=2.0,
    max_delay=10.0,
    timeout=30.0
)
