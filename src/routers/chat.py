from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Dict
from constants.prompt_library import SYSTEM_PROMPT
from core.chat_completion import generate_chat_completions
from core.tool_call import execute_query
from utils.google_search import get_google_search
from utils.conversation import get_history, extract_chat_history
router = APIRouter(prefix="/chat", tags=["chat"])

class ChatHistoryItem(BaseModel):
    user: str
    assistant: str

class Query(BaseModel):
    userid: int
    message: str
    token: str

class Question(BaseModel):
    text: str
@router.post("/chat_completion")
async def chat_completions(query: Query):
    # history_list = [item.dict() for item in query.history]
    history_list = extract_chat_history(get_history(userid=query.userid, token=query.token))
    # return StreamingResponse(generate_chat_completions(query.message))
    return {
        "message": await generate_chat_completions(query.userid, query.token, query.message, history_list)
    }

@router.post("/function_calling")
async def call_function(query: Question):
    return execute_query(query.text)

@router.post("/google_search")
async def do_google_search(query: Question):
    return await get_google_search(query.text)