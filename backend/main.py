from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

MODEL_NAME = "qwen2:1.5b"  # le modèle que tu as testé avec ollama

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"message": "Hello, backend is working"}

@app.post("/chat")
def chat(req: ChatRequest):
    prompt = (
        "Tu es un assistant. Réponds uniquement en français, de façon claire et courte.\n\n"
        f"Question: {req.message}\n"
        "Réponse:"
    )

    try:
        r = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        return {"answer": data.get("response", "").strip()}
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=500,
            detail="Ollama n'est pas lancé. Ouvre l'app Ollama puis réessaie.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
