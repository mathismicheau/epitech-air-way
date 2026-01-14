
from mcp.provider import get_flights
from mcp.model import process_user_message
from mcp.googleProvider import save_reservation_to_sheet

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



def handle_chat(message: str, last_search_results: list = None):
    # 1. Analyse de l'intention par l'IA
    result = process_user_message(message)

    # --- CAS : RECHERCHE DE VOLS ---
    if result["intent"] == "search":
        raw_flights = get_flights(result)
        flights = format_flight_data(raw_flights)

        if not flights:
            return {
                "answer": f"Aucun vol trouvé pour {result.get('destinationLocationCode')}.",
                "flights": []
            }

        # CORRECTION INDENTATION : On sort du "if not flights"
        prices = [float(f["price"]) for f in flights]
        
        return {
            "answer": (
                f"J'ai trouvé {len(flights)} vols vers {result['destinationLocationCode']} "
                f"le {result['departureDate']} à partir de {min(prices)} {flights[0]['currency']}."
            ),
            "flights": flights # On renvoie ça au React pour qu'il les affiche
        }

    # --- CAS : RÉSERVATION ---
    elif result["intent"] == "book":
        # ATTENTION : Ici, il faut normalement récupérer les infos du vol sélectionné.
        # Si tu es en test, on imagine que tu réserves le premier vol du dernier résultat.
        if last_search_results:
            flight_to_book = last_search_results[0] 
            success = save_reservation_to_sheet(flight_to_book)
            return {
                "answer": "C'est fait ! Votre réservation a été enregistrée dans le Google Sheet.",
                "status": "success"
            }
        else:
            return {"answer": "Quel vol souhaitez-vous réserver ? Je n'ai pas de recherche en cours."}

    # --- CAS : ERREUR / INCONNU ---
    return {"answer": "Je n'ai pas bien compris votre demande."}
