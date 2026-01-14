from __future__ import annotations

import json
import ollama

MODEL_NAME = "qwen3:1.7b"

# FLIGHTS
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

    if not data.get("originLocationCode") or not data.get("destinationLocationCode"):
        raise ValueError("Impossible d’extraire les aéroports de départ / arrivée.")

    return {
        "originLocationCode": data["originLocationCode"],
        "destinationLocationCode": data["destinationLocationCode"],
        "departureDate": data["departureDate"],
        "adults": int(data.get("adults", 1)),
    }


# HOTELS
def extract_hotel_query(message: str) -> dict:
    prompt = (
        "Tu extrais des informations d’hôtel.\n"
        "Réponds UNIQUEMENT en JSON à plat avec ces clés :\n"
        "city_name, checkin, checkout, adults, rooms.\n"
        "Dates = YYYY-MM-DD.\n"
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

    if not data.get("city_name"):
        raise ValueError("Ville manquante pour la recherche d’hôtel.")
    if not data.get("checkin") or not data.get("checkout"):
        raise ValueError("Dates checkin / checkout manquantes (YYYY-MM-DD).")

    return {
        "city_name": data["city_name"],
        "checkin": data["checkin"],
        "checkout": data["checkout"],
        "adults": int(data.get("adults", 2)),
        "rooms": int(data.get("rooms", 1)),
    }
