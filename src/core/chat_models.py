from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum

from constants.prompt_library import SYSTEM_PROMPT


class ModelProvider(Enum):
    """Supported LLM providers"""
    GEMINI = "gemini"
    OPENAI = "openai"
    TOGETHER = "together"


@dataclass
class ChatConfig:
    """Configuration for chat completion"""
    model_name: str = "gemini-2.0-flash"
    temperature: float = 0.7
    max_tokens: int = 5000
    enable_timing_logs: bool = True
    provider: ModelProvider = ModelProvider.GEMINI


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


@dataclass
class AsyncDataResult:
    """Result from async data fetching operations"""
    user_info: str
    task_history: str
    function_calling: Dict[str, Any]


@dataclass
class VectorStoreData:
    """Data from vector store queries"""
    about_us: str
    domain_knowledge: str
    time_management_tips: str


@dataclass
class ChatMetrics:
    """Performance metrics for chat completion"""
    total_time: float
    classification_time: float
    data_fetching_time: float
    message_formatting_time: float
    llm_inference_time: float
    background_task_time: float


class ChatCompletionError(Exception):
    """Custom exception for chat completion errors"""
    pass


class DataFetchError(ChatCompletionError):
    """Error during data fetching operations"""
    pass


class LLMInferenceError(ChatCompletionError):
    """Error during LLM inference"""
    pass 