from fastapi import FastAPI
from pydantic import BaseModel
from amadeus_http import search_flights
from services import ask_model_to_extract, format_flight_data

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    # 1️⃣ IA → extraction
    flight_query = ask_model_to_extract(req.message)

    # 2️⃣ Appel Amadeus HTTP (qui marche)
    raw_flights = search_flights(
        origin=flight_query["originLocationCode"],
        dest=flight_query["destinationLocationCode"],
        date=flight_query["departureDate"],
        adults=flight_query.get("adults", 1)
    )

    # 3️⃣ Format pour le front
    flights = format_flight_data(raw_flights)

    return {
        "query": flight_query,
        "flights": flights
    }
