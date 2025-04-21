from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from typing import Optional
from constants.prompt_library import SYSTEM_PROMPT
from core.chat_completion import generate_chat_completions
from core.tool_call import execute_query
from utils.google_search import get_google_search
from utils.conversation import get_history, extract_chat_history
from utils.vision import com_vision
from utils.chat import infer
from config import settings
router = APIRouter(prefix="/chat", tags=["chat"])

class ChatHistoryItem(BaseModel):
    user: str
    assistant: str

class Query(BaseModel):
    userid: int
    message: str
    token: str
    img_url: Optional[str] = None

class Question(BaseModel):
    text: str
    num_of_result: int

class Url(BaseModel):
    url: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 5000
    stream: Optional[bool] = False

@router.post("/chat_completion")
async def chat_completions(query: Query):
    # history_list = [item.dict() for item in query.history]
    history_list = extract_chat_history(get_history(userid=query.userid, token=query.token))
    # return StreamingResponse(generate_chat_completions(query.message))
    return {
        "message": await generate_chat_completions(query.userid, query.token, query.message, history_list, image_url=query.img_url)
    }

@router.post("/function_calling")
async def call_function(query: Question):
    return execute_query(query.text)

@router.post("/google_search")
async def do_google_search(query: Question):
    return await get_google_search(query.text, query.num_of_result)

@router.post("/vision")
async def get_vision(url: Url):
    return{"response": com_vision(url.url)}

@router.post("/v1/chat/completions")
async def gemini_openai_compatible(request: ChatCompletionRequest):
    """
    OpenAI-compatible endpoint that uses Gemini-2.0-Flash for inference
    """
    # Get configuration from environment variables

    if not settings.gemini_api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    try:
        # Format messages for the API
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Call the inference function
        response = await infer(
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url,
            model_name=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )

        # Return the response directly
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {str(e)}")