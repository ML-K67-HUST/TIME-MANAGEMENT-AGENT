import time
import asyncio
import functools
import logging
from typing import Any, Callable, TypeVar, Optional
from contextlib import asynccontextmanager

from .chat_models import ChatMetrics, ChatCompletionError

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class PerformanceTimer:
    """Context manager for timing operations with optional logging"""
    
    def __init__(self, operation_name: str, logger: logging.Logger, enabled: bool = True):
        self.operation_name = operation_name
        self.logger = logger
        self.enabled = enabled
        self.start_time = None
        self.elapsed_time = None
    
    def __enter__(self):
        if self.enabled:
            self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.enabled and self.start_time:
            self.elapsed_time = time.time() - self.start_time
            self.logger.info(f"{self.operation_name}: {self.elapsed_time:.4f}s")
    
    @property
    def time(self) -> float:
        """Get elapsed time in seconds"""
        return self.elapsed_time or 0.0


def with_error_handling(
    operation_name: str,
    default_return: Any = None,
    reraise: bool = False
):
    """Decorator for adding error handling to functions"""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {operation_name}: {e}")
                if reraise:
                    raise ChatCompletionError(f"{operation_name} failed: {e}") from e
                return default_return
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {operation_name}: {e}")
                if reraise:
                    raise ChatCompletionError(f"{operation_name} failed: {e}") from e
                return default_return
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def with_timing(operation_name: str, enabled: bool = True):
    """Decorator for adding timing to functions"""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with PerformanceTimer(operation_name, logger, enabled):
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with PerformanceTimer(operation_name, logger, enabled):
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


async def gather_with_error_handling(*coros, return_exceptions: bool = True):
    """
    Enhanced asyncio.gather with better error handling and logging
    """
    try:
        results = await asyncio.gather(*coros, return_exceptions=return_exceptions)
        
        # Log any exceptions found
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Coroutine {i} failed: {result}")
        
        return results
    except Exception as e:
        logger.error(f"gather_with_error_handling failed: {e}")
        raise


class BackgroundTaskManager:
    """Enhanced background task manager with better lifecycle management"""
    
    def __init__(self):
        self.background_tasks = set()
        self._shutdown = False
    
    async def schedule_task(self, coro, task_name: str = "unnamed"):
        """Schedule a background task with proper cleanup"""
        if self._shutdown:
            logger.warning(f"Cannot schedule task '{task_name}' - manager is shutdown")
            return
        
        loop = asyncio.get_running_loop()
        task = loop.create_task(coro, name=task_name)
        
        self.background_tasks.add(task)
        task.add_done_callback(self._task_done_callback)
        
        logger.debug(f"Scheduled background task: {task_name}")
        return task
    
    def _task_done_callback(self, task):
        """Callback when a background task completes"""
        self.background_tasks.discard(task)
        
        if task.cancelled():
            logger.debug(f"Background task {task.get_name()} was cancelled")
        elif task.exception():
            logger.error(f"Background task {task.get_name()} failed: {task.exception()}")
        else:
            logger.debug(f"Background task {task.get_name()} completed successfully")
    
    async def wait_for_completion(self, timeout: Optional[float] = None):
        """Wait for all background tasks to complete"""
        if not self.background_tasks:
            return
        
        try:
            await asyncio.wait_for(
                asyncio.gather(*self.background_tasks, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Background tasks did not complete within {timeout}s")
    
    async def shutdown(self, timeout: Optional[float] = 10.0):
        """Gracefully shutdown all background tasks"""
        self._shutdown = True
        
        if not self.background_tasks:
            return
        
        logger.info(f"Shutting down {len(self.background_tasks)} background tasks")
        
        # Cancel all tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for completion or timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*self.background_tasks, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Some background tasks did not shutdown within {timeout}s")
    
    @property
    def active_task_count(self) -> int:
        """Get the number of active background tasks"""
        return len(self.background_tasks)


def validate_context_data(data: dict, required_fields: list) -> bool:
    """Validate that required context data is present and not empty"""
    for field in required_fields:
        if field not in data or not data[field]:
            logger.warning(f"Missing or empty required field: {field}")
            return False
    return True


def sanitize_prompt(prompt: str, max_length: int = 10000) -> str:
    """Sanitize and truncate prompt if necessary"""
    if not prompt:
        return ""
    
    # Remove excessive whitespace
    sanitized = " ".join(prompt.split())
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
        logger.warning(f"Prompt truncated to {max_length} characters")
    
    return sanitized


def format_timing_summary(metrics: ChatMetrics) -> str:
    """Format timing metrics into a readable summary"""
    return (
        f"Chat Completion Timing Summary:\n"
        f"  Total: {metrics.total_time:.4f}s\n"
        f"  Classification: {metrics.classification_time:.4f}s\n"
        f"  Data Fetching: {metrics.data_fetching_time:.4f}s\n"
        f"  Message Formatting: {metrics.message_formatting_time:.4f}s\n"
        f"  LLM Inference: {metrics.llm_inference_time:.4f}s\n"
        f"  Background Tasks: {metrics.background_task_time:.4f}s"
    ) 