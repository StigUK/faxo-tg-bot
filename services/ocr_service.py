import json
import os

from google.cloud import vision
from google.oauth2 import service_account


def get_credentials():
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if service_account_json:
        service_account_info = json.loads(service_account_json)

        return service_account.Credentials.from_service_account_info(
            service_account_info
        )

    return None


def recognize_text(image_bytes: bytes) -> str:
    credentials = get_credentials()

    client = vision.ImageAnnotatorClient(
        credentials=credentials
    )

    image = vision.Image(content=image_bytes)

    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(response.error.message)

    if not response.text_annotations:
        return ""

    return response.text_annotations[0].description.strip()