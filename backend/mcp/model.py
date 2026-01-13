import json
import ollama


MODEL_NAME = "qwen3"

def ask_model_to_extract(message: str) -> dict:
    """
    Extrait les données à plat (sans sous-clé 'vol') et au format de date ISO.
    """
    current_date = "Aujourd'hui nous sommes le lundi 12 Janvier 2026."
    
    prompt = (
        f"{current_date}\n"
        "Tu dois extraire les informations de vol de la phrase utilisateur.\n"
        "CONSIGNES STRICTES :\n"
        "1. Les clés du JSON doivent être UNIQUEMENT: originLocationCode, destinationLocationCode, departureDate, adults.\n"
        "2. NE PAS créer de clé parente (comme 'vol' ou 'flight'). Le JSON doit être à plat.\n"
        "3. departureDate doit être au format YYYY-MM-DD (ex: 2026-01-20).\n"
        "4. originLocationCode et destinationLocationCode doivent être en codes IATA (3 lettres).\n"
        "5. adults doit être un nombre (1 par défaut).\n"
        f"Phrase : {message}"
    )

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            format='json',
            messages=[
                {'role': 'system', 'content': 'Tu es un extracteur de données strict. Tu réponds UNIQUEMENT en JSON à plat.'},
                {'role': 'user', 'content': prompt}
            ]
        )
        data = json.loads(response['message']['content'])
        
        # Sécurité : Si l'IA a quand même créé une clé 'vol', on l'aplatit
        
                
        print(f"Extraction IA : {data}")
        return data
    except Exception as e:
        print(f"Erreur IA : {e}")
        return {}
    

def extract_flight_query(message: str) -> dict:
    data = ask_model_to_extract(message)

    if not data.get("originLocationCode") or not data.get("destinationLocationCode"):
        raise ValueError("Extraction IA incomplète")

    return data
