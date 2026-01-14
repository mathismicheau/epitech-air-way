# Stockage en mémoire (simple pour dev)
sessions = {}

def get_session(session_id: str) -> dict:
    if session_id not in sessions:
        sessions[session_id] = {
            "flights": [],
            "last_query": None,
            "state": "idle"  # idle, awaiting_reservation
        }
    return sessions[session_id]

def update_session(session_id: str, data: dict):
    sessions[session_id].update(data)

def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]