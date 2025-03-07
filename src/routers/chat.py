from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Dict
from constants.prompt_library import SYSTEM_PROMPT
from core.chat import generate_chat_completions

router = APIRouter(prefix="/chat", tags=["chat"])

class Query(BaseModel):
    message: str
    history: List[Dict[str,str]] 

@router.post("/chat_completion")
async def chat_completions(query: Query):
    # return StreamingResponse(generate_chat_completions(query.message))
    return {
        "message": await generate_chat_completions(query.message, query.history)
    }
