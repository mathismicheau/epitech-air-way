from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Optional

from mcp.session import get_session, update_session
from mcp.googleProvider import save_reservation_to_sheet
from mcp.model import extract_flight_query, extract_hotel_query, process_user_message
from mcp.provider import search_flights, search_hotels

DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def _is_hotel_intent(text: str) -> bool:
    t = (text or "").lower()
    return ("hotel" in t) or ("hôtel" in t)


def _hotel_need_dates_answer() -> str:
    return (
        "Ok. Pour chercher un hôtel, j’ai besoin des dates.\n"
        "Donne-moi : check-in et check-out au format YYYY-MM-DD.\n"
        "Exemple : hotel Toulouse 2026-02-10 2026-02-12"
    )


def _flight_need_info_answer() -> str:
    return (
        "Ok. Pour chercher un vol, il me faut :\n"
        "- départ (code IATA, ex: TLS)\n"
        "- destination (code IATA, ex: CDG)\n"
        "- date (YYYY-MM-DD)\n"
        "Exemple : vol TLS CDG 2026-02-10"
    )


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


def _hotels_to_text(hotels: List[dict]) -> str:
    lines: List[str] = []
    for i, h in enumerate(hotels, start=1):
        name = h.get("name") or "Hotel"
        hid = h.get("id") or ""
        offer = h.get("cheapestOffer") or {}
        total = offer.get("total")
        cur = offer.get("currency")
        if total and cur:
            lines.append(f"{i}. {name} — {total} {cur} (id: {hid})")
        else:
            lines.append(f"{i}. {name} (id: {hid})")
    return "\n".join(lines)


def _flights_to_text(flights: List[dict]) -> str:
    lines: List[str] = []
    for i, f in enumerate(flights, start=1):
        airline = f.get("airline") or "-"
        dep = f.get("departure") or {}
        arr = f.get("arrival") or {}
        price = f.get("price")
        cur = f.get("currency") or ""
        dep_iata = dep.get("iata") or "-"
        arr_iata = arr.get("iata") or "-"
        dep_at = dep.get("at") or "-"
        arr_at = arr.get("at") or "-"
        if price is not None:
            lines.append(f"{i}. {airline} — {dep_iata} → {arr_iata} | {dep_at} → {arr_at} | {price} {cur}")
        else:
            lines.append(f"{i}. {airline} — {dep_iata} → {arr_iata} | {dep_at} → {arr_at}")
    return "\n".join(lines)


def handle_chat(message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    msg = (message or "").strip()
    lower = msg.lower()

    if not session_id:
        session_id = str(uuid.uuid4())

    session = get_session(session_id) or {}

    if _is_hotel_intent(lower):
        dates = DATE_RE.findall(msg)
        if len(dates) < 2:
            return {"session_id": session_id, "answer": _hotel_need_dates_answer()}

        try:
            query = extract_hotel_query(msg)
        except Exception:
            return {
                "session_id": session_id,
                "answer": "Je n’ai pas compris la ville et les dates. Exemple : hotel London 2026-02-10 2026-02-12",
            }

        try:
            raw_hotels = search_hotels(query)
            hotels = format_hotel_data(raw_hotels)
            if not hotels:
                return {
                    "session_id": session_id,
                    "answer": f"Aucun hôtel trouvé à {query['city_name']} du {query['checkin']} au {query['checkout']}.",
                }

            answer = (
                f"J’ai trouvé {len(hotels)} hôtels à {query['city_name']} du {query['checkin']} au {query['checkout']}.\n\n"
                f"{_hotels_to_text(hotels)}"
            )
            return {"session_id": session_id, "answer": answer}
        except Exception:
            return {"session_id": session_id, "answer": "Erreur lors de la recherche d’hôtels."}

    try:
        intent_data = process_user_message(msg)
        intent = intent_data.get("intent", "search")
    except Exception:
        intent = "search"
        intent_data = {}

    # ---- BOOK ----
    if intent == "book":
        flights = session.get("flights", [])
        query = session.get("last_query", {})
        
        # Vérifier qu'on a des vols en session
        if not flights:
            return {
                "session_id": session_id,
                "answer": "❌ Aucune recherche en cours. Cherchez d'abord un vol !",
                "flights": [],
                "hotels": []
            }
        
        # Récupérer le vol choisi (par défaut le premier)
        flight_index = intent_data.get("flight_index", 1) or 1  # <- intent_data au lieu de result
        selected_flight = flights[min(int(flight_index) - 1, len(flights) - 1)]
        
        # Créer la réservation
        reservation = {
            "id": str(uuid.uuid4())[:8],
            "nom": intent_data.get("nom") or "Non renseigné",  # <- intent_data
            "prenom": intent_data.get("prenom") or "Non renseigné",  # <- intent_data
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
                "hotels": [],
                "reserved": True
            }
        except Exception as e:
            return {
                "session_id": session_id,
                "answer": f"❌ Erreur lors de la réservation: {str(e)}",
                "flights": flights,
                "hotels": []
            }
            
    # ---- SEARCH (default) ----
    # Si process_user_message n'a pas rempli result, on repasse sur extract_flight_query.

    try:
        if intent_data and intent_data.get("intent") == "search" and intent_data.get("originLocationCode"):
            q = {
                "originLocationCode": intent_data["originLocationCode"],
                "destinationLocationCode": intent_data["destinationLocationCode"],
                "departureDate": intent_data["departureDate"],
                "adults": int(intent_data.get("adults", 1)),
                "max": 5,
            }
        else:
            extracted = extract_flight_query(msg)
            q = {
                "originLocationCode": extracted["originLocationCode"],
                "destinationLocationCode": extracted["destinationLocationCode"],
                "departureDate": extracted["departureDate"],
                "adults": int(extracted.get("adults", 1)),
                "max": 5,
            }

        raw_flights = search_flights(q)
        flights = format_flight_data(raw_flights)

        if not flights:
            return {
                "session_id": session_id,
                "answer": f"Aucun vol trouvé de {q['originLocationCode']} vers {q['destinationLocationCode']} le {q['departureDate']}.",
            }

        update_session(session_id, {"flights": flights, "last_query": q, "state": "awaiting_reservation"})

        answer = (
            f"J’ai trouvé {len(flights)} vols de {q['originLocationCode']} vers {q['destinationLocationCode']} le {q['departureDate']}.\n\n"
            f"{_flights_to_text(flights)}\n\n"
            "Dis : \"Je réserve le vol 1\" pour réserver."
        )
        return {"session_id": session_id, "answer": answer}

    except Exception:
        return {"session_id": session_id, "answer": _flight_need_info_answer()}
