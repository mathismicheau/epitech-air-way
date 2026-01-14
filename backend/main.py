from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from mcp.controller import handle_chat
from mcp.googleProvider import save_reservation_to_sheet

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
    session_id: Optional[str] = None  # <- Ajouter session_id

class ReservationRequest(BaseModel):
    id: str
    nom: str
    prenom: str
    lieuD: str
    lieuA: str
    dateD: str
    dateA: str
    nbr: int
    prix: str

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        return handle_chat(req.message, req.session_id)
    except Exception as e:
        return {"answer": f"Erreur: {str(e)}"}

@app.post("/reserve")
def reserve(req: ReservationRequest):
    try:
        save_reservation_to_sheet(req.dict())
        return {"success": True, "message": "Réservation enregistrée !"}
    except Exception as e:
        return {"success": False, "message": str(e)}