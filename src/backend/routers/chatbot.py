from fastapi import APIRouter
from pydantic import BaseModel
from src.backend.services.chatbot_service import chat

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str

@router.post("/")
def chat_endpoint(request: ChatRequest):
    response = chat(request.message)
    return {"response": response}

