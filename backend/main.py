from fastapi import FastAPI
from pydantic import BaseModel
from mcp.controller import handle_chat
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        return handle_chat(req.message)
    except Exception as e:
        return {"answer": "Erreur lors du traitement de la demande."}
