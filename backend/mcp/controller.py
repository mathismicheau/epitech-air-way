from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Optional

from mcp.session import get_session, update_session
from mcp.googleProvider import save_reservation_to_sheet
from mcp.recommender import get_activity_suggestions


# Extraction IA (new)
from mcp.model import extract_flight_query, extract_hotel_query, process_user_message, ask_model_to_process  # garde process_user_message si tu l'utilises
# Providers (Amadeus)
from mcp.provider import search_flights, search_hotels


# -----------------------------
# Regex + helpers UX
# -----------------------------
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


# -----------------------------
# Formatters (front-friendly)
# -----------------------------
def format_flight_data(raw_flights: List[dict]) -> List[dict]:
    """
    Transforme le JSON Amadeus Flight Offers en format léger pour React.
    """
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
    On renvoie un format simple et stable pour le front.
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


# -----------------------------
# Main controller (single entry)
# -----------------------------
def handle_chat(message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Contrat de réponse stable pour ton front :
    {
      "session_id": str,
      "answer": str,
      "flights": [],
      "hotels": [],
      "reserved": bool (optionnel)
    }
    """
    msg = (message or "").strip()
    lower = msg.lower()

    if not session_id:
        session_id = str(uuid.uuid4())
    try:
        analysis = ask_model_to_process(msg)
        intent = analysis.get("intent")
        if intent == "advice":
            return get_activity_suggestions(msg, session_id)
            
    except Exception:
        pass 

    session = get_session(session_id) or {}

    # =========================
    # 1) HOTELS (prioritaire si le texte contient hotel/hôtel)
    # =========================
    if _is_hotel_intent(lower):
        # UX rule: pas de dates => on demande (pas d'appel API)
        dates = DATE_RE.findall(msg)
        if len(dates) < 2:
            return {"session_id": session_id, "answer": _hotel_need_dates_answer(), "flights": [], "hotels": []}

        try:
            analysis = ask_model_to_process(msg)
            intent = analysis.get("intent")
            if intent == "hotel":
                 query=extract_hotel_query(msg)
        except Exception:
            return {
                "session_id": session_id,
                "answer": "Je n’ai pas compris la ville et les dates. Exemple : hotel Toulouse 2026-02-10 2026-02-12",
                "flights": [],
                "hotels": [],
            }

        try:
            raw_hotels = search_hotels(query)
            hotels = format_hotel_data(raw_hotels)

            if not hotels:
                return {
                    "session_id": session_id,
                    "answer": f"Aucun hôtel trouvé à {query['city_name']} du {query['checkin']} au {query['checkout']}.",
                    "flights": [],
                    "hotels": [],
                }

            return {
                "session_id": session_id,
                "answer": f"J’ai trouvé {len(hotels)} hôtels à {query['city_name']} du {query['checkin']} au {query['checkout']}.",
                "flights": [],
                "hotels": hotels,
            }

        except Exception:
            return {
                "session_id": session_id,
                "answer": "Erreur lors de la recherche d’hôtels (provider indisponible ou paramètres invalides).",
                "flights": [],
                "hotels": [],
            }

    # =========================
    # 2) FLIGHTS (search / book) via IA intent
    # =========================
    # Si tu veux garder ton système "book", on utilise process_user_message.
    # Sinon, tu peux ignorer intent et faire direct extract_flight_query.
    try:
        result = process_user_message(msg)  # doit renvoyer intent + infos
        intent = result.get("intent", "search")
    except Exception:
        # fallback: simple mode search
        intent = "search"
        result = {}

    # ---- BOOK ----
    if intent == "book":
        flights = session.get("flights", [])
        last_query = session.get("last_query", {})

        if not flights:
            return {
                "session_id": session_id,
                "answer": "❌ Aucune recherche en cours. Cherche d’abord un vol (ex: vol TLS CDG 2026-02-10).",
                "flights": [],
                "hotels": [],
            }

        flight_index = result.get("flight_index", 1) or 1
        try:
            idx = max(int(flight_index) - 1, 0)
        except Exception:
            idx = 0
        selected = flights[min(idx, len(flights) - 1)]

        reservation = {
            "id": str(uuid.uuid4())[:8],
            "nom": result.get("nom") or "Non renseigné",
            "prenom": result.get("prenom") or "Non renseigné",
            "lieuD": (selected.get("departure") or {}).get("iata"),
            "lieuA": (selected.get("arrival") or {}).get("iata"),
            "dateD": (selected.get("departure") or {}).get("at"),
            "dateA": (selected.get("arrival") or {}).get("at"),
            "nbr": last_query.get("adults", 1),
            "prix": f"{selected.get('price')}{selected.get('currency')}",
        }

        try:
            save_reservation_to_sheet(reservation)
            update_session(session_id, {"flights": [], "last_query": None, "state": "idle"})

            return {
                "session_id": session_id,
                "answer": (
                    "✅ Réservation confirmée !\n"
                    f"Vol {selected.get('airline')} : {reservation['lieuD']} → {reservation['lieuA']}\n"
                    f"Départ: {reservation['dateD']}\n"
                    f"Prix: {reservation['prix']}\n"
                    f"Référence: {reservation['id']}"
                ),
                "flights": [],
                "hotels": [],
                "reserved": True,
            }
        except Exception as e:
            return {
                "session_id": session_id,
                "answer": f"❌ Erreur lors de la réservation : {str(e)}",
                "flights": flights,
                "hotels": [],
            }

    # ---- SEARCH (default) ----
    # Si process_user_message n'a pas rempli result, on repasse sur extract_flight_query.
    try:
        if not result or "originLocationCode" not in result:
            result = extract_flight_query(msg)
            result["max"] = 5

        raw_flights = search_flights(
            {
                "originLocationCode": result["originLocationCode"],
                "destinationLocationCode": result["destinationLocationCode"],
                "departureDate": result["departureDate"],
                "adults": int(result.get("adults", 1)),
                "max": int(result.get("max", 5)),
            }
        )
        flights = format_flight_data(raw_flights)

        if not flights:
            return {
                "session_id": session_id,
                "answer": f"Aucun vol trouvé de {result.get('originLocationCode')} vers {result.get('destinationLocationCode')}.",
                "flights": [],
                "hotels": [],
            }

        update_session(
            session_id,
            {"flights": flights, "last_query": result, "state": "awaiting_reservation"},
        )

        # message UX simple (sans emojis si tu préfères)
        lines = []
        for i, f in enumerate(flights):
            lines.append(
                f"Vol {i+1} - {f.get('airline')} | {f['departure']['iata']} → {f['arrival']['iata']} | {f.get('price')} {f.get('currency')}"
            )

        answer = (
            f"J’ai trouvé {len(flights)} vols pour {result['destinationLocationCode']} le {result['departureDate']}.\n"
            + "\n".join(lines)
            + "\n\nDis : \"Je réserve le vol 1\" pour réserver."
        )

        return {"session_id": session_id, "answer": answer, "flights": flights, "hotels": []}

    except Exception:
        return {
            "session_id": session_id,
            "answer": _flight_need_info_answer(),
            "flights": [],
            "hotels": [],
        }
