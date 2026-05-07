from google.cloud import vision


def recognize_text(image_bytes: bytes) -> str:
    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=image_bytes)

    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(response.error.message)

    if not response.text_annotations:
        return ""

    return response.text_annotations[0].description.strip()