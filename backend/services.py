import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

def ask_model(message: str) -> str:
    prompt = (
        "Tu es un assistant spécialisé dans l’aviation. "
        "Réponds en français, de façon claire et concise.\n"
        f"Question : {message}\n"
        "Réponse :"
    )

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    data = response.json()
    return data.get("response", "Erreur lors de la génération")
