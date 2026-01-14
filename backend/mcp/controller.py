from mcp.session import get_session, update_session
from mcp.provider import get_flights
from mcp.model import process_user_message
from mcp.googleProvider import save_reservation_to_sheet
import uuid

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



def handle_chat(message: str, session_id: str = None):

    if not session_id:
        session_id = str(uuid.uuid4())
    
    session = get_session(session_id)
    # 1. Analyse de l'intention par l'IA
    result = process_user_message(message)
    intent = result.get("intent", "search")

    if intent == "book":
            flights = session.get("flights", [])
            query = session.get("last_query", {})
            
            # Vérifier qu'on a des vols en session
            if not flights:
                return {
                    "session_id": session_id,
                    "answer": "❌ Aucune recherche en cours. Cherchez d'abord un vol !",
                    "flights": []
                }
            
            # Récupérer le vol choisi (par défaut le premier)
            flight_index = result.get("flight_index", 1) or 1
            selected_flight = flights[min(int(flight_index) - 1, len(flights) - 1)]
            
            # Créer la réservation
            reservation = {
                "id": str(uuid.uuid4())[:8],
                "nom": result.get("nom") or "Non renseigné",
                "prenom": result.get("prenom") or "Non renseigné",
                "lieuD": selected_flight["departure"]["iata"],
                "lieuA": selected_flight["arrival"]["iata"],
                "dateD": selected_flight["departure"]["at"],
                "dateA": selected_flight["arrival"]["at"],
                "nbr": query.get("adults", 1),
                "prix": f"{selected_flight['price']}{selected_flight['currency']}"
            }
            
            # Sauvegarder dans Google Sheets
            try:
                save_reservation_to_sheet(reservation)
                
                # Reset session
                update_session(session_id, {"flights": [], "last_query": None, "state": "idle"})
                
                return {
                    "session_id": session_id,
                    "answer": (
                        f"✅ Réservation confirmée !\n"
                        f"Vol {selected_flight['airline']} : {reservation['lieuD']} → {reservation['lieuA']}\n"
                        f"Départ: {reservation['dateD']}\n"
                        f"Prix: {reservation['prix']}\n"
                        f"Référence: {reservation['id']}"
                    ),
                    "flights": [],
                    "reserved": True
                }
            except Exception as e:
                return {
                    "session_id": session_id,
                    "answer": f"❌ Erreur lors de la réservation: {str(e)}",
                    "flights": flights
                }
        
        # 3. RECHERCHE DE VOL
    if intent == "search":
            try:
                raw_flights = get_flights(result)
                flights = format_flight_data(raw_flights)
                
                if not flights:
                    return {
                        "session_id": session_id,
                        "answer": f"Aucun vol trouvé de {result['originLocationCode']} vers {result['destinationLocationCode']}.",
                        "flights": []
                    }
                
                # Sauvegarder dans la session
                update_session(session_id, {
                    "flights": flights,
                    "last_query": result,
                    "state": "awaiting_reservation"
                })
                
                prices = [float(f["price"]) for f in flights]
                
                flights_text = "\n".join([
                    f"✈️ Vol {i+1} - {f['airline']} | {f['departure']['iata']} → {f['arrival']['iata']} | {f['price']} {f['currency']}"
                    for i, f in enumerate(flights)
                ])
                
                return {
                    "session_id": session_id,
                    "answer": (
                        f"J'ai trouvé {len(flights)} vols vers {result['destinationLocationCode']} "
                        f"le {result['departureDate']} à partir de {min(prices)} {flights[0]['currency']}.\n\n"
                        f"{flights_text}\n\n"
                        f"Dites 'Je réserve le vol 1' pour réserver !"
                    ),
                    "flights": flights
                }
            except Exception as e:
                return {
                    "session_id": session_id,
                    "answer": f"Erreur: {str(e)}",
                    "flights": []
                }
        
        # 4. AUTRE
        
    return {
            "session_id": session_id,
            "answer": "Je peux vous aider à chercher un vol. Dites-moi votre destination !",
            "flights": []
        }