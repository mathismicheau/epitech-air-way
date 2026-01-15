import ollama
from mcp.model import MODEL_NAME

def get_activity_suggestions(message: str, session_id: str = None):
    """Génère des suggestions touristiques via Llama 3."""
    system_prompt = (
        "Tu es Wingman, un guide de voyage expert. L'utilisateur te demande des conseils, "
        "des idées de visites ou des suggestions d'activités. Réponds de manière "
        "chaleureuse en français avec 3-4 suggestions précises et des emojis."
    )
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ]
        )
        return {
            "session_id": session_id,
            "answer": response['message']['content'],
            "flights": [],
            "hotels": []
        }
    except Exception as e:
        return {
            "session_id": session_id,
            "answer": f"Désolé, je ne peux pas répondre pour le moment : {str(e)}",
            "flights": [],
            "hotels": []
        }