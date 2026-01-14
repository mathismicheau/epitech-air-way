from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1pJRBN0mEt4xiMCGKicFff04mqrJEC4KF9B7J7h9e6Qc"
RANGE_NAME = "reservation!A:I"  # adapte si besoin
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "famous-empire-477209-f1-eec914cd4569.json")

def save_reservation_to_sheet(data: dict):
    creds = Credentials.from_service_account_file(
        CREDENTIALS_PATH,  # <- Utilise le chemin absolu
        scopes=SCOPES
    )

    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    values = [[
        data["id"],
        data["nom"],
        data["prenom"],
        data["lieuD"],
        data["lieuA"],
        data["dateD"],
        data["dateA"],
        data["nbr"],
        data["prix"],
    ]]

    body = {
        "values": values
    }

    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
