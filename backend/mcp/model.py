import json
import ollama


MODEL_NAME = "qwen3"

def ask_model_to_process(message: str) -> dict:
    current_date = "Aujourd'hui nous sommes le lundi 12 Janvier 2026."
    
    prompt = (
        f"{current_date}\n"
        "Analyse le message de l'utilisateur pour déterminer s'il veut RECHERCHER un vol ou RÉSERVER un vol.\n\n"
        "CONSIGNES DE RÉPONSE JSON :\n"
        "1. Ajoute une clé 'intent' qui vaut soit 'search' soit 'book'.\n"
        "2. Si intent == 'search' : 2.1 Les clés du JSON doivent être UNIQUEMENT: originLocationCode, destinationLocationCode, departureDate, adults. 2.2 NE PAS créer de clé parente (comme 'vol' ou 'flight'). Le JSON doit être à plat. 2.3 departureDate doit être au format YYYY-MM-DD (ex: 2026-01-20). 2.4 originLocationCode et destinationLocationCode doivent être en codes IATA (3 lettres majuscules) 2.4 adults doit être un nombre (1 par défaut).\n"
        "3. Si intent == 'book' : l'utilisateur veut confirmer une réservation (ex: 'Réserve ce vol', 'Je prends celui-là').\n"
        "4. Format de date : YYYY-MM-DD.\n"
        f"Phrase : {message}"
    )

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            format='json',
            messages=[
                {'role': 'system', 'content': 'Tu es un assistant de voyage. Tu réponds UNIQUEMENT en JSON.'},
                {'role': 'user', 'content': prompt}
            ]
        )
        return json.loads(response['message']['content'])
    except Exception as e:
        print(f"Erreur IA : {e}")
        return {}

# def ask_model_to_extract(message: str) -> dict:
#     """
#     Extrait les données à plat (sans sous-clé 'vol') et au format de date ISO.
#     """
#     current_date = "Aujourd'hui nous sommes le lundi 12 Janvier 2026."
    
#     prompt = (
#         f"{current_date}\n"
#         "Tu dois extraire les informations de vol de la phrase utilisateur.\n"
#         "CONSIGNES STRICTES :\n"
#         "1. Les clés du JSON doivent être UNIQUEMENT: originLocationCode, destinationLocationCode, departureDate, adults.\n"
#         "2. NE PAS créer de clé parente (comme 'vol' ou 'flight'). Le JSON doit être à plat.\n"
#         "3. departureDate doit être au format YYYY-MM-DD (ex: 2026-01-20).\n"
#         "4. originLocationCode et destinationLocationCode doivent être en codes IATA (3 lettres majuscules).\n"
#         "5. adults doit être un nombre (1 par défaut).\n"
#         f"Phrase : {message}"
#     )

#     try:
#         response = ollama.chat(
#             model=MODEL_NAME,
#             format='json',
#             messages=[
#                 {'role': 'system', 'content': 'Tu es un extracteur de données strict. Tu réponds UNIQUEMENT en JSON à plat.'},
#                 {'role': 'user', 'content': prompt}
#             ]
#         )
#         data = json.loads(response['message']['content'])
        
#         # Sécurité : Si l'IA a quand même créé une clé 'vol', on l'aplatit
        
                
#         print(f"Extraction IA : {data}")
#         return data
#     except Exception as e:
#         print(f"Erreur IA : {e}")
#         return {}
    

def process_user_message(message: str) -> dict:
    # 1. On appelle le modèle qui détecte l'intention ET extrait les données
    data = ask_model_to_process(message)
    
    intent = data.get("intent")

    # 2. Logique selon l'intention
    if intent == "search":
        # On vérifie que les données de recherche sont là
        if not data.get("originLocationCode") or not data.get("destinationLocationCode"):
            # Si l'IA a détecté une recherche mais n'a pas trouvé les villes
            return {"intent": "error", "message": "Détails de recherche manquants (villes/dates)."}
        return data

    elif intent == "book":
        # Pour une réservation, on n'a pas forcément besoin de codes IATA dans la phrase
        # car on se basera sur le dernier vol affiché (le contexte).
        return {"intent": "book", "message": "Demande de réservation détectée"}

    else:
        return {"intent": "unknown", "message": "Je n'ai pas compris si vous voulez chercher ou réserver."}