from __future__ import annotations

import json
from datetime import datetime
import locale

import ollama

# ✅ Un seul modèle (celui que tu as déjà et qui marche chez toi)
MODEL_NAME = "llama3"


# -----------------------
# Locale/date (juste pour aider l'IA)
# -----------------------
def _safe_set_french_locale() -> None:
    try:
        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    except Exception:
        try:
            locale.setlocale(locale.LC_TIME, "fr_FR")
        except Exception:
            # Si la locale FR n'existe pas sur la machine, on ignore
            pass


_safe_set_french_locale()


def get_current_date() -> str:
    now = datetime.now()
    return f"Aujourd'hui nous sommes le {now.strftime('%A %d %B %Y')}."


# -----------------------
# 1) INTENT (vol) : search vs book
# -----------------------
def ask_model_to_process(message: str) -> dict:
    """
    Détermine l'intention de l'utilisateur:
    - intent = 'search' (recherche de vol) + extraction des champs vol
    - intent = 'book' (réservation)
    """
    current_date = get_current_date()

    prompt = (
        f"{current_date}\n"
        "Analyse le message de l'utilisateur pour déterminer s'il veut RECHERCHER un vol ou RÉSERVER un vol.\n\n"
        "CONSIGNES JSON STRICTES :\n"
        "1) Ajoute une clé 'intent' qui vaut soit 'search' soit 'book'.\n"
        "2) Si intent == 'search' : réponds en JSON à plat avec UNIQUEMENT ces clés :\n"
        "   intent, originLocationCode, destinationLocationCode, departureDate, adults.\n"
        "   - originLocationCode / destinationLocationCode : codes IATA (3 lettres majuscules)\n"
        "   - departureDate : YYYY-MM-DD\n"
        "   - adults : nombre (1 par défaut)\n"
        "3) Si intent == 'book' : réponds en JSON à plat avec UNIQUEMENT : intent.\n"
        f"Phrase : {message}"
    )

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            format="json",
            messages=[
                {"role": "system", "content": "Tu es un assistant de voyage. Tu réponds UNIQUEMENT en JSON valide."},
                {"role": "user", "content": prompt},
            ],
        )
        return json.loads(response["message"]["content"])
    except Exception as e:
        print(f"Erreur IA (process) : {e}")
        return {}


def process_user_message(message: str) -> dict:
    """
    Utilisé par le controller 'session' pour gérer 'search' vs 'book'.
    """
    data = ask_model_to_process(message)
    intent = data.get("intent")

    if intent == "search":
        # Validation minimale des champs vols
        if not data.get("originLocationCode") or not data.get("destinationLocationCode") or not data.get("departureDate"):
            return {"intent": "error", "message": "Détails de recherche manquants (départ/destination/date)."}
        # default adults
        if "adults" not in data or data["adults"] in (None, ""):
            data["adults"] = 1
        return data

    if intent == "book":
        return {"intent": "book"}

    return {"intent": "unknown", "message": "Je n'ai pas compris si vous voulez chercher ou réserver."}


# -----------------------
# 2) EXTRACTION VOL pure (utile si tu bypass intent)
# -----------------------
def extract_flight_query(message: str) -> dict:
    prompt = (
        "Tu extrais des informations de vol.\n"
        "Réponds UNIQUEMENT en JSON à plat avec ces clés :\n"
        "originLocationCode, destinationLocationCode, departureDate, adults.\n"
        "origin/destination = codes IATA (ex: TLS, CDG).\n"
        "departureDate = YYYY-MM-DD.\n"
        "adults = nombre (1 par défaut).\n\n"
        f"Phrase : {message}"
    )

    response = ollama.chat(
        model=MODEL_NAME,
        format="json",
        messages=[
            {"role": "system", "content": "Tu réponds uniquement en JSON valide."},
            {"role": "user", "content": prompt},
        ],
    )

    data = json.loads(response["message"]["content"])

    if not data.get("originLocationCode") or not data.get("destinationLocationCode") or not data.get("departureDate"):
        raise ValueError("Impossible d’extraire départ/destination/date pour le vol.")

    return {
        "originLocationCode": data["originLocationCode"],
        "destinationLocationCode": data["destinationLocationCode"],
        "departureDate": data["departureDate"],
        "adults": int(data.get("adults", 1)),
    }


# -----------------------
# 3) EXTRACTION HOTEL (Amadeus) : ville + dates obligatoires
# -----------------------
def extract_hotel_query(message: str) -> dict:
    prompt = (
        "Tu extrais des informations d’hôtel.\n"
        "Réponds UNIQUEMENT en JSON à plat avec ces clés :\n"
        "city_name, checkin, checkout, adults, rooms.\n"
        "Dates = YYYY-MM-DD.\n"
        "ATTENTION : si checkin/checkout ne sont pas présents dans la phrase, mets null.\n"
        "adults = 2 par défaut, rooms = 1 par défaut.\n\n"
        f"Phrase : {message}"
    )

    response = ollama.chat(
        model=MODEL_NAME,
        format="json",
        messages=[
            {"role": "system", "content": "Tu réponds uniquement en JSON valide."},
            {"role": "user", "content": prompt},
        ],
    )

    data = json.loads(response["message"]["content"])

    # defaults
    adults = data.get("adults", 2)
    rooms = data.get("rooms", 1)

    city_name = data.get("city_name")
    checkin = data.get("checkin")
    checkout = data.get("checkout")

    if not city_name:
        raise ValueError("Ville manquante pour la recherche d’hôtel.")
    # dates obligatoires pour déclencher la recherche (le controller peut déjà bloquer avant)
    if not checkin or not checkout:
        raise ValueError("Dates checkin / checkout manquantes (YYYY-MM-DD).")

    return {
        "city_name": city_name,
        "checkin": checkin,
        "checkout": checkout,
        "adults": int(adults),
        "rooms": int(rooms),
    }
