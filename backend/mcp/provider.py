from __future__ import annotations

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# CONFIG
CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
FLIGHTS_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

CITY_SEARCH_URL = "https://test.api.amadeus.com/v1/reference-data/locations"
HOTEL_LIST_URL = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
HOTEL_OFFERS_URL = "https://test.api.amadeus.com/v3/shopping/hotel-offers"


# AUTH
def get_token() -> str:
    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"]


# FLIGHTS
def search_flights(query: dict):
    token = get_token()

    r = requests.get(
        FLIGHTS_URL,
        headers={"Authorization": f"Bearer {token}"},
        params=query,
        timeout=20,
    )
    r.raise_for_status()
    return r.json().get("data", [])


# HOTELS
def city_name_to_city_code(city_name: str) -> str:
    token = get_token()

    r = requests.get(
        CITY_SEARCH_URL,
        headers={"Authorization": f"Bearer {token}"},
        params={"subType": "CITY", "keyword": city_name},
        timeout=15,
    )
    r.raise_for_status()

    data = r.json().get("data", [])
    if not data:
        raise ValueError(f"Ville inconnue : {city_name}")

    return data[0]["iataCode"]


def search_hotels(query: dict):
    token = get_token()

    city_code = city_name_to_city_code(query["city_name"])

    r1 = requests.get(
        HOTEL_LIST_URL,
        headers={"Authorization": f"Bearer {token}"},
        params={"cityCode": city_code},
        timeout=20,
    )
    r1.raise_for_status()

    hotels = r1.json().get("data", [])[:10]
    hotel_ids = [h["hotelId"] for h in hotels if "hotelId" in h]

    if not hotel_ids:
        return []

    r2 = requests.get(
        HOTEL_OFFERS_URL,
        headers={"Authorization": f"Bearer {token}"},
        params={
            "hotelIds": ",".join(hotel_ids),
            "checkInDate": query["checkin"],
            "checkOutDate": query["checkout"],
            "adults": query["adults"],
            "roomQuantity": query["rooms"],
        },
        timeout=30,
    )
    r2.raise_for_status()

    return r2.json().get("data", [])
