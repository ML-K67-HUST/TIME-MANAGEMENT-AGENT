import asyncio
import time
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import logging
from contextlib import asynccontextmanager

from config import settings
from constants.prompt_library import SYSTEM_PROMPT
from core.tool_call import execute_query_if_needed
from utils.conversation import update_history
from utils.user_cache import (
    get_cached_user_info, 
    get_cached_task_history, 
    should_invalidate_task_cache, 
    invalidate_task_cache
)
from utils.chat import infer
from utils.classifier import classify_prompt
from utils.vision import com_vision
from rag.query_from_vector_store import (
    query_for_about_us,
    query_for_domain_knowledge,
    query_for_task_management_tips
)
from utils.format_message import get_current_time_info
from database.discord import send_discord_notification
from config import settings

logger = logging.getLogger(__name__)


@dataclass
class ChatConfig:
    """Configuration for chat completion"""
    model_name: str = settings.main_llm_model
    temperature: float = 0.7
    max_tokens: int = 5000
    enable_timing_logs: bool = True


@dataclass
class ChatContext:
    """Context data for chat completion"""
    userid: int
    token: str
    prompt: str
    history: List[Dict[str, str]]
    image_url: Optional[str] = None
    system_prompt: str = SYSTEM_PROMPT


@dataclass
class ProcessedContext:
    """Processed context data ready for LLM"""
    now: str
    user_info: str
    task_history: str
    function_calling_result: str
    about_us: str
    domain_knowledge: str
    time_management_tips: str
    img_info: str


class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name: str, logger: logging.Logger, enabled: bool = True):
        self.operation_name = operation_name
        self.logger = logger
        self.enabled = enabled
        self.start_time = None
    
    def __enter__(self):
        if self.enabled:
            self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.enabled and self.start_time:
            elapsed = time.time() - self.start_time
            self.logger.info(f"{self.operation_name}: {elapsed:.4f}s")


class ChatDataFetcher:
    """Handles fetching all required data for chat completion"""
    
    @staticmethod
    async def fetch_async_data(context: ChatContext, decider: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch all async data concurrently"""
        
        async def get_user_info():
            return get_cached_user_info(context.userid, context.token)
        
        async def get_task_history():
            return get_cached_task_history(context.userid, context.token)
        
        async def execute_function_call():
            return execute_query_if_needed(
                userid=context.userid,
                query=context.prompt,
                decider=decider["function_calling"]
            )
        
        # Execute all async operations concurrently
        user_info, task_history, function_calling = await asyncio.gather(
            get_user_info(),
            get_task_history(),
            execute_function_call(),
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(user_info, Exception):
            logger.error(f"Error fetching user info: {user_info}")
            user_info = ""
        
        if isinstance(task_history, Exception):
            logger.error(f"Error fetching task history: {task_history}")
            task_history = ""
            
        if isinstance(function_calling, Exception):
            logger.error(f"Error in function calling: {function_calling}")
            function_calling = {"result": ""}
        
        return {
            "user_info": user_info,
            "task_history": task_history,
            "function_calling": function_calling
        }
    
    @staticmethod
    def fetch_vector_store_data(prompt: str, decider: Dict[str, Any]) -> Dict[str, str]:
        """Fetch data from vector stores"""
        return {
            "about_us": query_for_about_us(prompt, decider=decider["about_us"]),
            "domain_knowledge": query_for_domain_knowledge(prompt, decider=decider["domain_knowledge"]),
            "time_management_tips": query_for_task_management_tips(prompt, decider=decider["task_management"])
        }
    
    @staticmethod
    async def process_image(image_url: Optional[str]) -> str:
        """Process image if provided"""
        if image_url and image_url.startswith("http"):
            try:
                return com_vision(image_url)
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                return "Error processing image"
        return "No image provided"


class MessageFormatter:
    """Handles message formatting for LLM"""
    
    @staticmethod
    def format_system_prompt(context: ChatContext, processed: ProcessedContext) -> str:
        """Format the system prompt with all context data"""
        return context.system_prompt.format(
            NOW_TIME=processed.now,
            MESSAGE=processed.function_calling_result,
            ABOUT_US=processed.about_us,
            USER_INFO=processed.user_info,
            TASK_HISTORY=processed.task_history,
            TIME_MANAGEMENT=processed.time_management_tips,
            DOMAIN_KNOWLEDGE=processed.domain_knowledge,
            PICTURE_DESCRIPTION=processed.img_info
        )
    
    @staticmethod
    def build_messages(context: ChatContext, formatted_system_prompt: str) -> List[Dict[str, str]]:
        """Build the complete message list for LLM"""
        messages = [{"role": "system", "content": formatted_system_prompt}]
        
        # Add conversation history
        for message in context.history:
            messages.extend([
                {"role": "user", "content": message["user"]},
                {"role": "assistant", "content": message["assistant"]}
            ])
        
        # Add current prompt
        messages.append({"role": "user", "content": context.prompt})
        
        return messages


class BackgroundTaskManager:
    """Manages background tasks"""
    
    def __init__(self):
        self.background_tasks = set()
    
    async def schedule_update_task(self, userid: int, token: str, prompt: str, assistant: str):
        """Schedule background task for updating history and cache"""
        loop = asyncio.get_running_loop()
        
        async def update_task():
            try:
                update_history(userid=userid, token=token, user=prompt, assistant=assistant)
                
                if should_invalidate_task_cache(prompt):
                    invalidate_task_cache(userid, token)
                    
            except Exception as e:
                logger.error(f"Error in background task: {e}")
        
        task = loop.create_task(update_task())
        self.background_tasks.add(task)
        task.add_done_callback(lambda t: self.background_tasks.discard(t))


# Global background task manager
background_manager = BackgroundTaskManager()


class ChatCompletionService:
    """Main service for handling chat completions"""
    
    def __init__(self, config: ChatConfig = None):
        self.config = config or ChatConfig()
        self.data_fetcher = ChatDataFetcher()
        self.message_formatter = MessageFormatter()
    
    async def generate_completion(self, context: ChatContext) -> str:
        """Generate chat completion with optimized structure"""
        
        with PerformanceTimer("Total chat completion", logger, self.config.enable_timing_logs):
            try:
                # Step 1: Classify prompt
                with PerformanceTimer("Prompt classification", logger, self.config.enable_timing_logs):
                    decider = classify_prompt(context.prompt)
                    logger.info(f"Prompt classification: {decider}")
                
                # Step 2: Fetch all required data
                processed_context = await self._fetch_all_data(context, decider)
                
                # Step 3: Format messages
                with PerformanceTimer("Message formatting", logger, self.config.enable_timing_logs):
                    formatted_system_prompt = self.message_formatter.format_system_prompt(
                        context, processed_context
                    )
                    messages = self.message_formatter.build_messages(context, formatted_system_prompt)
                
                # Step 4: Send Discord notification (if needed)
                send_discord_notification(context.prompt, formatted_system_prompt)
                logger.info(f"System prompt size: {len(formatted_system_prompt)} characters")
                
                # Step 5: Get LLM response
                with PerformanceTimer("LLM inference", logger, self.config.enable_timing_logs):
                    response = await self._get_llm_response(messages)
                
                # Step 6: Schedule background tasks
                await background_manager.schedule_update_task(
                    context.userid, context.token, context.prompt, response
                )
                
                return response
                
            except Exception as e:
                logger.error(f"Error in chat completion: {e}")
                raise
    
    async def _fetch_all_data(self, context: ChatContext, decider: Dict[str, Any]) -> ProcessedContext:
        """Fetch and process all required data"""
        
        # Fetch current time
        with PerformanceTimer("Get current time", logger, self.config.enable_timing_logs):
            now = get_current_time_info()
        
        # Fetch async data concurrently
        with PerformanceTimer("Async data fetching", logger, self.config.enable_timing_logs):
            async_data = await self.data_fetcher.fetch_async_data(context, decider)
        
        # Fetch vector store data
        with PerformanceTimer("Vector store queries", logger, self.config.enable_timing_logs):
            vector_data = self.data_fetcher.fetch_vector_store_data(context.prompt, decider)
        
        # Process image
        with PerformanceTimer("Image processing", logger, self.config.enable_timing_logs):
            img_info = await self.data_fetcher.process_image(context.image_url)
        
        return ProcessedContext(
            now=now,
            user_info=async_data["user_info"],
            task_history=async_data["task_history"],
            function_calling_result=async_data["function_calling"].get("result", ""),
            about_us=vector_data["about_us"],
            domain_knowledge=vector_data["domain_knowledge"],
            time_management_tips=vector_data["time_management_tips"],
            img_info=img_info
        )
    
    async def _get_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from LLM"""
        response = await infer(
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url,
            model_name=self.config.model_name,
            messages=messages
        )
        return response.choices[0].message.content


# Public API function (maintains backward compatibility)
async def generate_chat_completions(
    userid: int,
    token: str,
    prompt: str,
    history: List[Dict[str, str]] = None,
    image_url: Optional[str] = None,
    system_prompt: str = SYSTEM_PROMPT
) -> str:
    """
    Generate chat completion with improved structure and error handling.
    
    Args:
        userid: User ID
        token: User token
        prompt: User prompt
        history: Conversation history
        image_url: Optional image URL
        system_prompt: System prompt template
        
    Returns:
        Assistant response
    """
    if history is None:
        history = []
    
    context = ChatContext(
        userid=userid,
        token=token,
        prompt=prompt,
        history=history,
        image_url=image_url,
        system_prompt=system_prompt
    )
    
    service = ChatCompletionService()
    return await service.generate_completion(context) 