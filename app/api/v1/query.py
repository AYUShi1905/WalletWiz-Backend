from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.dependencies import get_current_user
from models.db_user import User
from models.request import ChatRequest
from models.response import ChatResponse
from services import query_processor as query_service

# Initialize the rate limiter using the client's remote IP address
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["Conversational Agent"])

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat_session(
    request: Request,  # Request parameter is required by slowapi decorators
    payload: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Unified conversational interface for WalletWiz.
    Processes user messages, maintains context, and executes tool calls
    (logging expenses or querying databases) using Gemini 2.5 Flash.
    
    Rate limited to 20 requests per minute per IP address.
    """
    return await query_service.process_chat(
        user_id=current_user.id,
        message=payload.message,
        history=payload.history
    )
