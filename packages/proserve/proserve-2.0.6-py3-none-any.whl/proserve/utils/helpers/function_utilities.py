"""
ProServe Function Utilities and Decorators
Handles execution timing, retry logic, and function utilities
"""

import time
from typing import Callable, Any


def measure_execution_time(func: Callable) -> Callable:
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        from .string_utilities import format_duration
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} executed in {format_duration(execution_time)}")
        return result
    return wrapper


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry function on failure"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise e
                    
                    print(f"Attempt {attempt} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
        
        return wrapper
    return decorator
