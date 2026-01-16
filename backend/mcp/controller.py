from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Optional

from mcp.session import get_session, update_session
from mcp.recommender import get_activity_suggestions
from mcp.googleProvider import save_reservation_to_sheet
from mcp.model import ask_model_to_process, extract_flight_query, extract_hotel_query, process_user_message
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

    # 1. ANALYSE DE L'INTENTION PAR L'IA (LLM)
    analysis = {}
    try:
        analysis = ask_model_to_process(msg)
        intent = analysis.get("intent")
        
        # Cas spécifique : Suggestions d'activités
        if intent == "advice":
            return get_activity_suggestions(msg, session_id)
            
    except Exception as e:
        print(f"Erreur analyse IA : {e}")
        intent = None

    # Récupération de la session actuelle
    session = get_session(session_id) or {}

    # 2. FOLLOW-UP : Infos de chambre (Si on attendait une réponse oui/non)
    if session.get("state") == "awaiting_room_details":
        if _is_yes(msg):
            payload = session.get("room_details_payload") or []
            if not payload:
                update_session(session_id, {"state": "idle", "room_details_payload": []})
                return {"session_id": session_id, "answer": "Je n’ai pas d’infos chambre supplémentaires."}

            answer = _room_details_to_text(payload)
            update_session(session_id, {"state": "idle", "room_details_payload": []})
            return {"session_id": session_id, "answer": answer}

        if _is_no(msg):
            update_session(session_id, {"state": "idle", "room_details_payload": []})
            return {"session_id": session_id, "answer": "Ok, je reste sur ces résultats."}

    # 3. INTENTION HÔTEL (Détectée par mot-clé OU par l'IA)
    if _is_hotel_intent(lower) or intent == "hotel":
        dates = DATE_RE.findall(msg)
        if len(dates) < 2:
            return {"session_id": session_id, "answer": _hotel_need_dates_answer()}

        try:
            query = extract_hotel_query(msg)
            raw_hotels = search_hotels(query)
            hotels = format_hotel_data(raw_hotels)

            if not hotels:
                return {
                    "session_id": session_id,
                    "answer": f"Aucun hôtel trouvé à {query['city_name']} du {query['checkin']} au {query['checkout']}.",
                }

            # Préparation des détails de chambre pour le follow-up
            with_room = [
                {"name": h.get("name"), "roomDetails": h.get("roomDetails")}
                for h in hotels if h.get("roomDetails")
            ]

            answer = (
                f"🏨 Hôtels trouvés à {query['city_name']} du {query['checkin']} au {query['checkout']} :\n\n"
                f"{_hotels_to_text(hotels)}"
            )

            if with_room:
                answer += "\n\nJ'ai trouvé des détails sur les chambres (lits, conditions). Voulez-vous les voir ? (oui/non)"
                update_session(session_id, {
                    "state": "awaiting_room_details", 
                    "room_details_payload": with_room[:5]
                })
            else:
                update_session(session_id, {"state": "idle", "room_details_payload": []})

            return {"session_id": session_id, "answer": answer}
        except Exception as e:
            return {"session_id": session_id, "answer": f"Erreur lors de la recherche d'hôtel : {str(e)}"}

    # 4. INTENTION RÉSERVATION DE VOL (Book)
    if intent == "book":
        flights = session.get("flights", [])
        last_q = session.get("last_query", {})

        if not flights:
            return {"session_id": session_id, "answer": "❌ Cherchez d'abord un vol avant de réserver !"}

        try:
            # On récupère les infos via l'analyse déjà faite par ask_model_to_process
            idx_str = analysis.get("flight_index", 1)
            idx = max(int(idx_str) - 1, 0)
            selected = flights[min(idx, len(flights) - 1)]

            reservation = {
                "id": str(uuid.uuid4())[:8],
                "nom": analysis.get("nom") or "Inconnu",
                "prenom": analysis.get("prenom") or "Inconnu",
                "lieuD": selected["departure"]["iata"],
                "lieuA": selected["arrival"]["iata"],
                "dateD": selected["departure"]["at"],
                "dateA": selected["arrival"]["at"],
                "nbr": last_q.get("adults", 1),
                "prix": f"{selected['price']} {selected['currency']}",
            }

            save_reservation_to_sheet(reservation)
            update_session(session_id, {"flights": [], "last_query": None, "state": "idle"})

            return {
                "session_id": session_id, 
                "answer": f"✅ Réservation confirmée ! Réf: {reservation['id']}\nVol: {reservation['lieuD']} → {reservation['lieuA']}"
            }
        except Exception as e:
            return {"session_id": session_id, "answer": f"Erreur réservation : {str(e)}"}

    # 5. RECHERCHE DE VOL (Search / Par défaut)
    try:
        # On tente d'utiliser les données extraites par l'IA si dispo, sinon on force l'extraction
        if intent == "search" and analysis.get("originLocationCode"):
            q = {
                "originLocationCode": analysis["originLocationCode"],
                "destinationLocationCode": analysis["destinationLocationCode"],
                "departureDate": analysis["departureDate"],
                "adults": int(analysis.get("adults", 1)),
                "max": 5
            }
        else:
            # Fallback sur l'extracteur manuel
            q = extract_flight_query(msg)
            q["max"] = 5

        raw_flights = search_flights(q)
        flights = format_flight_data(raw_flights)

        if not flights:
            return {"session_id": session_id, "answer": "Aucun vol trouvé pour ces critères."}

        update_session(session_id, {"flights": flights, "last_query": q, "state": "awaiting_reservation"})
        
        return {
            "session_id": session_id, 
            "answer": f"✈️ Vols trouvés ({q['originLocationCode']} -> {q['destinationLocationCode']}) :\n\n{_flights_to_text(flights)}"
        }

    except Exception:
        # Si rien n'a matché et que l'extraction de vol échoue aussi
        return {"session_id": session_id, "answer": _flight_need_info_answer()}