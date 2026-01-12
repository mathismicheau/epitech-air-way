
from fastapi import FastAPI, HTTPException
from models import ChatRequest
from services import ask_model

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Backend FastAPI opérationnel"}

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        answer = ask_model(req.message)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))