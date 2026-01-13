from fastapi import FastAPI
from pydantic import BaseModel
from mcp.controller import handle_chat
from mcp.googleProvider import save_reservation_to_sheet

app = FastAPI()

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