import os
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


HEADERS = [
    "published_at",
    "race_datetime",
    "left_number",
    "right_number",
    "rt_left",
    "rt_right",
    "et_left",
    "et_right",
    "time_left",
    "time_right",
    "ft_left",
    "ft_right",
    "speed_left",
    "speed_right",
]


def get_client():
    credentials = Credentials.from_service_account_file(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        scopes=SCOPES,
    )

    return gspread.authorize(credentials)


def get_or_create_worksheet(spreadsheet):
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        worksheet = spreadsheet.worksheet(today)

    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=today,
            rows=1000,
            cols=20,
        )

        worksheet.append_row(HEADERS)

    return worksheet


def append_result_to_sheet(data: dict):
    client = get_client()

    spreadsheet = client.open_by_key(
        os.getenv("GOOGLE_SHEET_ID")
    )

    worksheet = get_or_create_worksheet(spreadsheet)

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data["race_datetime"],
        data["left_number"],
        data["right_number"],
        data["rt_left"],
        data["rt_right"],
        data["et_left"],
        data["et_right"],
        data["time_left"],
        data["time_right"],
        data["ft_left"],
        data["ft_right"],
        data["speed_left"],
        data["speed_right"],
    ]

    worksheet.append_row(row)