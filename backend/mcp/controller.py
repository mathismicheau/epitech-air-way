from __future__ import annotations

import re
from typing import Any, Dict, List

from mcp.model import extract_flight_query, extract_hotel_query
from mcp.provider import search_flights, search_hotels

# Helpers intent + validation
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def _is_hotel_intent(text: str) -> bool:
    t = (text or "").lower()
    return ("hotel" in t) or ("hôtel" in t)


def _hotel_need_dates_answer() -> str:
    return (
        "Ok 🙂 Pour chercher un hôtel, j’ai besoin des dates.\n"
        "Donne-moi : check-in et check-out au format YYYY-MM-DD.\n"
        "Exemple : hotel Toulouse 2026-02-10 2026-02-12"
    )


def _flight_need_info_answer() -> str:
    return (
        "Ok 🙂 Pour chercher un vol, il me faut :\n"
        "- départ (code IATA, ex: TLS)\n"
        "- destination (code IATA, ex: CDG)\n"
        "- date (YYYY-MM-DD)\n"
        "Exemple : vol TLS CDG 2026-02-10"
    )


# Formatters (front-friendly)
def format_flight_data(raw_flights: List[dict]) -> List[dict]:
    formatted: List[dict] = []

    for flight in raw_flights or []:
        if not isinstance(flight, dict):
            continue

        itineraries = flight.get("itineraries") or []
        if not itineraries or not isinstance(itineraries, list) or not isinstance(itineraries[0], dict):
            continue

        segments = itineraries[0].get("segments") or []
        if not segments or not isinstance(segments, list):
            continue

        first_seg = segments[0] if isinstance(segments[0], dict) else None
        last_seg = segments[-1] if isinstance(segments[-1], dict) else None
        if not first_seg or not last_seg:
            continue

        dep = first_seg.get("departure") or {}
        arr = last_seg.get("arrival") or {}

        airline_codes = flight.get("validatingAirlineCodes") or []
        airline = airline_codes[0] if airline_codes else None

        price_obj = flight.get("price") or {}
        total = price_obj.get("total")
        currency = price_obj.get("currency")

        formatted.append(
            {
                "id": flight.get("id"),
                "airline": airline,
                "departure": {"iata": dep.get("iataCode"), "at": dep.get("at")},
                "arrival": {"iata": arr.get("iataCode"), "at": arr.get("at")},
                "price": total,
                "currency": currency,
                "stops": max(len(segments) - 1, 0),
            }
        )

    return formatted


def format_hotel_data(raw_hotels: Any) -> List[dict]:
    """
    Amadeus Hotel Offers v3:
    - data[] items contain {"hotel": {...}, "offers": [...]}
    """
    items = raw_hotels if isinstance(raw_hotels, list) else []
    formatted: List[dict] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        hotel = item.get("hotel") or {}
        offers = item.get("offers") or []

        hotel_id = hotel.get("hotelId") or hotel.get("id")
        name = hotel.get("name")
        city_code = hotel.get("cityCode") or hotel.get("iataCode")

        cheapest_offer = None
        if isinstance(offers, list) and offers:
            def _offer_total(o: dict) -> float:
                try:
                    return float((o.get("price") or {}).get("total"))
                except Exception:
                    return 10**18

            offer_dicts = [o for o in offers if isinstance(o, dict)]
            best = min(offer_dicts, key=_offer_total, default=None)
            if best:
                p = best.get("price") or {}
                cheapest_offer = {
                    "total": p.get("total"),
                    "currency": p.get("currency"),
                    "checkInDate": best.get("checkInDate"),
                    "checkOutDate": best.get("checkOutDate"),
                }

        formatted.append(
            {
                "id": hotel_id,
                "name": name,
                "cityCode": city_code,
                "cheapestOffer": cheapest_offer,
            }
        )

    return formatted


# Main controller
def handle_chat(message: str) -> Dict[str, Any]:
    msg = (message or "").strip()
    lower = msg.lower()

    # HOTELS
    if _is_hotel_intent(lower):
        dates = DATE_RE.findall(msg)
        if len(dates) < 2:
            return {"answer": _hotel_need_dates_answer(), "hotels": [], "flights": []}

        try:
            query = extract_hotel_query(msg)
        except Exception:
            return {
                "answer": "Je n’ai pas réussi à comprendre la ville et les dates. Peux-tu reformuler ? (ex: hotel Toulouse 2026-02-10 2026-02-12)",
                "hotels": [],
                "flights": [],
            }

        try:
            raw_hotels = search_hotels(query)
            hotels = format_hotel_data(raw_hotels)

            if not hotels:
                return {
                    "answer": f"Aucun hôtel trouvé à {query['city_name']} du {query['checkin']} au {query['checkout']}.",
                    "hotels": [],
                    "flights": [],
                }

            return {
                "answer": f"J’ai trouvé {len(hotels)} hôtels à {query['city_name']} du {query['checkin']} au {query['checkout']}.",
                "hotels": hotels,
                "flights": [],
            }

        except Exception:
            return {
                "answer": "Erreur lors de la recherche d’hôtels (provider indisponible ou paramètres invalides).",
                "hotels": [],
                "flights": [],
            }

    # FLIGHTS
    try:
        query = extract_flight_query(msg)
    except Exception:
        return {"answer": _flight_need_info_answer(), "hotels": [], "flights": []}

    try:
        raw_flights = search_flights(
            {
                "originLocationCode": query["originLocationCode"],
                "destinationLocationCode": query["destinationLocationCode"],
                "departureDate": query["departureDate"],
                "adults": query.get("adults", 1),
                "max": 5,
            }
        )
        flights = format_flight_data(raw_flights)

        if not flights:
            return {
                "answer": f"Aucun vol trouvé entre {query['originLocationCode']} et {query['destinationLocationCode']} le {query['departureDate']}.",
                "hotels": [],
                "flights": [],
            }
        prices: List[float] = []
        for f in flights:
            try:
                if f.get("price") is not None:
                    prices.append(float(f["price"]))
            except Exception:
                pass

        currency = flights[0].get("currency") or ""
        if prices:
            answer = (
                f"J’ai trouvé {len(flights)} vols de {query['originLocationCode']} vers {query['destinationLocationCode']} "
                f"le {query['departureDate']} à partir de {min(prices)}{currency}."
            )
        else:
            answer = (
                f"J’ai trouvé {len(flights)} vols de {query['originLocationCode']} vers {query['destinationLocationCode']} "
                f"le {query['departureDate']}."
            )

        return {"answer": answer, "hotels": [], "flights": flights}

    except Exception:
        return {
            "answer": "Erreur lors de la recherche de vols (provider indisponible ou paramètres invalides).",
            "hotels": [],
            "flights": [],
        }
