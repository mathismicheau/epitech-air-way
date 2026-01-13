import requests
import os
from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
FLIGHTS_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"


def get_token():
    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    r.raise_for_status()
    return r.json()["access_token"]


def search_flights(origin, dest, date, adults=1, max_results=5):
    token = get_token()

    r = requests.get(
        FLIGHTS_URL,
        headers={"Authorization": f"Bearer {token}"},
        params={
            "originLocationCode": origin,
            "destinationLocationCode": dest,
            "departureDate": date,
            "adults": adults,
            "max": max_results
        }
    )
    r.raise_for_status()
    return r.json()["data"]


def get_flights(query: dict):
    return search_flights(
        origin=query["originLocationCode"],
        dest=query["destinationLocationCode"],
        date=query["departureDate"],
        adults=query.get("adults", 1)
    )
