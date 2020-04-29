import datetime
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

DATA_FILE = "google_api_data.json"
SHEET_NAME = "Google Code-in 2019 Winners Handbook"
OUTPUT_FILE = "birthdays.json"


def updateFile():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(DATA_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).get_worksheet(0)

    people = sheet.get_all_records()
    birthdays = []
    for p in people:
        if isinstance(p["Date of Birth"], int) or not len(str(p["Date of Birth"])):
            continue
        temp = {
            "name": p["Name"].strip(),
            "tz": p["Timezone"],
            "dob": p["Date of Birth"],  # format: %d.%m.%Y
            "username": p["Telegram"].strip(),
        }
        birthdays.append(temp)

        json.dump(
            birthdays,
            open(OUTPUT_FILE, "w+", encoding="utf-8"),
            ensure_ascii=False,
            indent=4,
        )


if __name__ == "__main__":
    updateFile()
