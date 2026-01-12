import os
import json
import ollama
from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()

amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET"),
    hostname="test"
)

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
        if "vol" in data:
            adults = data.get("adults", 1)
            data = data["vol"]
            if "adults" not in data:
                data["adults"] = adults
                
        print(f"Extraction IA (Nettoyée) : {data}")
        return data
    except Exception as e:
        print(f"Erreur IA : {e}")
        return {}
    

def format_flight_data(raw_flights):
    """Transforme le gros JSON Amadeus en format léger pour ton React."""
    formatted = []
    for flight in raw_flights:
        itinerary = flight['itineraries'][0]
        segments = itinerary['segments']
        formatted.append({
            "id": flight['id'],
            "airline": flight['validatingAirlineCodes'][0],
            "departure": {"iata": segments[0]['departure']['iataCode'], "at": segments[0]['departure']['at']},
            "arrival": {"iata": segments[-1]['arrival']['iataCode'], "at": segments[-1]['arrival']['at']},
            "price": flight['price']['total'],
            "currency": flight['price']['currency']
        })
    return formatted


def get_flights(flight_info: dict):
    try:
        origin = flight_info.get("originLocationCode")
        dest = flight_info.get("destinationLocationCode")
        date = flight_info.get("departureDate")
        passengers = int(flight_info.get("adults", 1))

        if not origin or not dest or not date:
            raise ValueError("Paramètres manquants")

        print(f"DEBUG - HTTP Amadeus: {origin} → {dest} | {date}")

        res = amadeus.get(
            "/v2/shopping/flight-offers",
            params={
                "originLocationCode": origin,
                "destinationLocationCode": dest,
                "departureDate": date,
                "adults": passengers,
                "max": 5
            }
        )

        print("DEBUG - Flights trouvés:", len(res.data))
        return format_flight_data(res.data[:3])

    except Exception as e:
        print("ERREUR FINALE:", e)
        return []
