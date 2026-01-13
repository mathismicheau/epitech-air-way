from mcp.model import extract_flight_query
from mcp.provider import get_flights

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



def handle_chat(message: str):
    # 1. IA
    query = extract_flight_query(message)

    # 2. Provider
    raw_flights = get_flights(query)

    # 3. Formatting
    flights = format_flight_data(raw_flights)

    if not flights:
        return {
            "answer": f"Aucun vol trouvé entre {query['originLocationCode']} et {query['destinationLocationCode']}.",
            "flights": []
        }

    prices = [float(f["price"]) for f in flights]

    return {
        "answer": (
            f"J'ai trouvé {len(flights)} vols de {query['originLocationCode']} "
            f"vers {query['destinationLocationCode']} le {query['departureDate']} "
            f"à partir de {min(prices)}{flights[0]['currency']}."
        ),
        "flights": flights
    }
