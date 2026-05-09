from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from agent import chat

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        result = chat(messages)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))