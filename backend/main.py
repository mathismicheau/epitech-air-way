from fastapi import FastAPI
from pydantic import BaseModel
from mcp.controller import handle_chat

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        return handle_chat(req.message)
    except Exception as e:
        return {"answer": "Erreur lors du traitement de la demande."}
