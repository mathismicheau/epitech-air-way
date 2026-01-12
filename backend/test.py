import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

def get_token():
    r = requests.post(
        "https://test.api.amadeus.com/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    print("TOKEN STATUS:", r.status_code)
    print("TOKEN BODY:", r.text)

    r.raise_for_status()
    return r.json()["access_token"]


def get_flights_http(origin, dest, date, adults=1):
    token = get_token()

    r = requests.get(
        "https://test.api.amadeus.com/v2/shopping/flight-offers",
        headers={
            "Authorization": f"Bearer {token}"
        },
        params={
            "originLocationCode": origin,
            "destinationLocationCode": dest,
            "departureDate": date,
            "adults": adults,
            "max": 5
        }
    )

    print("FLIGHTS STATUS:", r.status_code)
    print("FLIGHTS BODY:", r.text)

    r.raise_for_status()
    return r.json()
