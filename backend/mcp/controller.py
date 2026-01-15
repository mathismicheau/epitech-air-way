from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Optional

from mcp.session import get_session, update_session
from mcp.googleProvider import save_reservation_to_sheet
from mcp.model import extract_flight_query, extract_hotel_query, process_user_message
from mcp.provider import search_flights, search_hotels

DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

YES_WORDS = {"oui", "ok", "okay", "yes", "ouais", "yep", "d'accord", "dac", "vas-y", "go"}
NO_WORDS = {"non", "no", "nop", "pas besoin", "nan", "nope"}


def _is_yes(text: str) -> bool:
    t = (text or "").strip().lower()
    return t in YES_WORDS or any(t.startswith(w) for w in YES_WORDS)


def _is_no(text: str) -> bool:
    t = (text or "").strip().lower()
    return t in NO_WORDS or any(t.startswith(w) for w in NO_WORDS)


def _safe_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        return 10**18


def _fmt_dt(at: Any) -> str:
    s = str(at or "").strip()
    if "T" in s:
        s = s.replace("T", " ")
    return s[:16] if len(s) >= 16 else (s or "-")


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


# ---------------------------
# FORMAT / TRI DES DONNÉES
# ---------------------------

def format_flight_data(raw_flights: List[dict]) -> List[dict]:
    formatted: List[dict] = []
    for flight in raw_flights or []:
        if not isinstance(flight, dict):
            continue

        itineraries = flight.get("itineraries") or []
        if not itineraries or not isinstance(itineraries, list) or not isinstance(itineraries[0], dict):
            continue

        it0 = itineraries[0]
        segments = it0.get("segments") or []
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
                "priceValue": _safe_float(total),
                "currency": currency,
                "stops": max(len(segments) - 1, 0),
                "duration": it0.get("duration"),  # ex: PT1H20M (si présent)
            }
        )

    # TRI : du moins cher au plus cher
    formatted.sort(key=lambda x: x.get("priceValue", 10**18))
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

        # Choisir l'offre la moins chère
        cheapest_offer = None
        room_details = None

        if isinstance(offers, list) and offers:
            offer_dicts = [o for o in offers if isinstance(o, dict)]

            def _offer_total(o: dict) -> float:
                try:
                    return float((o.get("price") or {}).get("total"))
                except Exception:
                    return 10**18

            best = min(offer_dicts, key=_offer_total, default=None)
            if best:
                p = best.get("price") or {}
                cheapest_offer = {
                    "total": p.get("total"),
                    "currency": p.get("currency"),
                    "checkInDate": best.get("checkInDate"),
                    "checkOutDate": best.get("checkOutDate"),
                }

                # ROOM INFO (si dispo)
                # Amadeus renvoie parfois "room", "policies", "rateFamilyEstimated", etc.
                room = best.get("room")
                policies = best.get("policies")
                board = best.get("boardType") or best.get("boardTypeCode")

                room_details = {}
                if isinstance(room, dict):
                    rt = room.get("typeEstimated") or {}
                    if isinstance(rt, dict):
                        if rt.get("category"):
                            room_details["category"] = rt.get("category")
                        if rt.get("beds"):
                            room_details["beds"] = rt.get("beds")
                        if rt.get("bedType"):
                            room_details["bedType"] = rt.get("bedType")
                    desc = room.get("description")
                    if isinstance(desc, dict) and desc.get("text"):
                        room_details["description"] = desc.get("text")

                if board:
                    room_details["boardType"] = board

                if isinstance(policies, dict):
                    if policies.get("cancellation"):
                        room_details["cancellation"] = policies.get("cancellation")
                    if policies.get("paymentType"):
                        room_details["paymentType"] = policies.get("paymentType")

                # Nettoyage : si rien d'intéressant
                if not room_details:
                    room_details = None

        formatted.append(
            {
                "id": hotel_id,
                "name": name,
                "cityCode": city_code,
                "cheapestOffer": cheapest_offer,
                "priceValue": _safe_float((cheapest_offer or {}).get("total")),
                "roomDetails": room_details,
            }
        )

    # TRI : du moins cher au plus cher
    formatted.sort(key=lambda x: x.get("priceValue", 10**18))
    return formatted


# ---------------------------
# RENDU TEXTE (PROPRE)
# ---------------------------

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
        dep_at = _fmt_dt(dep.get("at"))
        arr_at = _fmt_dt(arr.get("at"))
        stops = f.get("stops", 0)

        tag = " (Le moins cher)" if i == 1 else ""
        price_txt = f"{price} {cur}".strip() if price is not None else "-"

        lines.append(
            f"{i}. {airline}{tag}\n"
            f"   - Trajet : {dep_iata} → {arr_iata}\n"
            f"   - Départ : {dep_at}\n"
            f"   - Arrivée : {arr_at}\n"
            f"   - Escales : {stops}\n"
            f"   - Prix : {price_txt}"
        )
    return "\n".join(lines)


def _hotels_to_text(hotels: List[dict]) -> str:
    lines: List[str] = []
    for i, h in enumerate(hotels, start=1):
        name = h.get("name") or "Hotel"
        offer = h.get("cheapestOffer") or {}
        total = offer.get("total")
        cur = offer.get("currency")
        checkin = offer.get("checkInDate")
        checkout = offer.get("checkOutDate")

        tag = " (Le moins cher)" if i == 1 else ""
        lines.append(f"{i}. {name}{tag}")

        if total and cur:
            lines.append(f"   - Prix : {total} {cur}")
        if checkin and checkout:
            lines.append(f"   - Dates : {checkin} → {checkout}")

        # On n'affiche pas les room details ici, on propose un follow-up si dispo
        lines.append("")  # ligne vide entre hôtels

    return "\n".join(lines).rstrip()


def _room_details_to_text(room_details_by_hotel: List[dict]) -> str:
    """
    room_details_by_hotel: liste d'objets {name, roomDetails}
    """
    lines: List[str] = ["Voici les infos chambre que j’ai trouvées :\n"]
    for i, item in enumerate(room_details_by_hotel, start=1):
        name = item.get("name") or f"Hôtel {i}"
        details = item.get("roomDetails") or {}
        lines.append(f"{i}. {name}")
        if details.get("category"):
            lines.append(f"   - Catégorie : {details.get('category')}")
        if details.get("beds"):
            lines.append(f"   - Lits : {details.get('beds')}")
        if details.get("bedType"):
            lines.append(f"   - Type de lit : {details.get('bedType')}")
        if details.get("boardType"):
            lines.append(f"   - Pension : {details.get('boardType')}")
        if details.get("paymentType"):
            lines.append(f"   - Paiement : {details.get('paymentType')}")
        if details.get("cancellation"):
            lines.append(f"   - Annulation : {details.get('cancellation')}")
        if details.get("description"):
            # on garde court
            desc = str(details.get("description"))
            lines.append(f"   - Description : {desc[:220]}{'…' if len(desc) > 220 else ''}")
        lines.append("")
    return "\n".join(lines).rstrip()


# ---------------------------
# MAIN HANDLER /CHAT
# ---------------------------

def handle_chat(message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    msg = (message or "").strip()
    lower = msg.lower()

    if not session_id:
        session_id = str(uuid.uuid4())

    session = get_session(session_id) or {}

    # ---- FOLLOW-UP : room details ----
    # Si le bot a proposé "Tu veux les infos de la chambre ?" et que l'utilisateur répond oui/non
    if session.get("state") == "awaiting_room_details":
        if _is_yes(msg):
            payload = session.get("room_details_payload") or []
            if not payload:
                update_session(session_id, {"state": "idle", "room_details_payload": []})
                return {"session_id": session_id, "answer": "Je n’ai pas d’infos chambre supplémentaires à afficher."}

            answer = _room_details_to_text(payload)
            update_session(session_id, {"state": "idle", "room_details_payload": []})
            return {"session_id": session_id, "answer": answer}

        if _is_no(msg):
            update_session(session_id, {"state": "idle", "room_details_payload": []})
            return {"session_id": session_id, "answer": "Ok, je te laisse les résultats comme ça."}

        return {
            "session_id": session_id,
            "answer": "Tu veux que je t’affiche les infos de la chambre ? Réponds juste par oui / non.",
        }

    # ---- HOTEL INTENT (keyword simple) ----
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

            # Préparer un payload room details (si on en a)
            with_room = [
                {"name": h.get("name"), "roomDetails": h.get("roomDetails")}
                for h in hotels
                if h.get("roomDetails")
            ]

            answer = (
                f"🏨 Hôtels trouvés à {query['city_name']} du {query['checkin']} au {query['checkout']} "
                f"(triés du moins cher au plus cher) :\n\n"
                f"{_hotels_to_text(hotels)}"
            )

            if with_room:
                answer += "\n\nJ’ai aussi des infos sur la chambre (lit, conditions, etc.). Tu veux que je te les affiche ? (oui/non)"
                update_session(
                    session_id,
                    {"state": "awaiting_room_details", "room_details_payload": with_room[:5]},
                )
            else:
                update_session(session_id, {"state": "idle", "room_details_payload": []})

            return {"session_id": session_id, "answer": answer}

        except Exception:
            return {"session_id": session_id, "answer": "Erreur lors de la recherche d’hôtels."}

    # ---- INTENT VIA IA (vol: search/book) ----
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

        if not flights:
            return {
                "session_id": session_id,
                "answer": "❌ Aucune recherche en cours. Cherche d'abord un vol !",
                "flights": [],
                "hotels": [],
            }

        flight_index = intent_data.get("flight_index", 1) or 1
        try:
            idx = max(int(flight_index) - 1, 0)
        except Exception:
            idx = 0

        selected_flight = flights[min(idx, len(flights) - 1)]

        reservation = {
            "id": str(uuid.uuid4())[:8],
            "nom": intent_data.get("nom") or "Non renseigné",
            "prenom": intent_data.get("prenom") or "Non renseigné",
            "lieuD": selected_flight["departure"]["iata"],
            "lieuA": selected_flight["arrival"]["iata"],
            "dateD": selected_flight["departure"]["at"],
            "dateA": selected_flight["arrival"]["at"],
            "nbr": query.get("adults", 1),
            "prix": f"{selected_flight['price']}{selected_flight['currency']}",
        }

        try:
            save_reservation_to_sheet(reservation)

            update_session(session_id, {"flights": [], "last_query": None, "state": "idle"})

            return {
                "session_id": session_id,
                "answer": (
                    "✅ Réservation confirmée !\n"
                    f"Vol {selected_flight['airline']} : {reservation['lieuD']} → {reservation['lieuA']}\n"
                    f"Départ : {_fmt_dt(reservation['dateD'])}\n"
                    f"Arrivée : {_fmt_dt(reservation['dateA'])}\n"
                    f"Prix : {reservation['prix']}\n"
                    f"Référence : {reservation['id']}"
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
            f"✈️ Vols trouvés de {q['originLocationCode']} vers {q['destinationLocationCode']} le {q['departureDate']} "
            f"(triés du moins cher au plus cher) :\n\n"
            f"{_flights_to_text(flights)}\n\n"
            'Dis : "Je réserve le vol 1" pour réserver.'
        )
        return {"session_id": session_id, "answer": answer}

    except Exception:
        return {"session_id": session_id, "answer": _flight_need_info_answer()}
