from fastapi import FastAPI
from pydantic import BaseModel
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
        return handle_chat(req.message)
    except Exception as e:
        return {"answer": "Erreur lors du traitement de la demande."}

@app.post("/reserve")
def reserve(req: ReservationRequest):
    try:
        save_reservation_to_sheet(req.dict())
        return {"success": True, "message": "Réservation enregistrée !"}
    except Exception as e:
        return {"success": False, "message": str(e)}