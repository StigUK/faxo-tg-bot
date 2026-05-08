# FAXO Drag Times Bot

Telegram bot for automatic OCR recognition of VINRACE drag racing slips using Google Vision API.

The bot:
- receives photos in Telegram;
- recognizes VINRACE timing slips;
- extracts race data;
- formats and publishes results to a Telegram channel;
- saves all race results to Google Sheets automatically.

---

## Features

- VINRACE OCR recognition
- Automatic Telegram channel posting
- Google Sheets integration
- Daily worksheets auto-generation
- RL / RT / ET / TIME / 60FT / SPEED parsing
- Race datetime detection
- Webhook support for Cloud Run
- Google Vision API support
- Invalid image protection
- Runtime logging

---

## Example Output

```text
🏁 VINRACE RESULT

🕒 14.09.2025 18:11:28

LEFT: NOT REG      RIGHT: 179

RL: NO             RL: NO
RT: 0,88           RT: 0,7
ET: 12,959         ET: 13,179
TIME: 13,839       TIME: 13,879
60FT: 2,471        60FT: 1,863
SPEED: 2,63        SPEED: 2,62
```

---

## Tech Stack

- Python 3.12
- aiogram
- Google Vision API
- Google Sheets API
- Cloud Run
- Docker

---

## Environment Variables

Create `.env` file:

```env
BOT_TOKEN=
CHANNEL_ID=
ACCESS_PASSWORD=

GOOGLE_SHEET_ID=
GOOGLE_SERVICE_ACCOUNT_JSON=

WEBHOOK_SECRET=
WEBHOOK_PATH=
WEBHOOK_BASE_URL=
```

---

## Local Development

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run bot locally

```bash
python bot_local.py
```

---

## Cloud Run Deployment

### Docker Build

```bash
docker build -t faxo-tg-bot .
```

### Deploy to Cloud Run

Use:
- Dockerfile build
- Public access enabled
- Port 8080

---

## Google Vision API Setup

Enable APIs:
- Cloud Vision API
- Google Sheets API

Create a Google Cloud Service Account and pass credentials through:

```env
GOOGLE_SERVICE_ACCOUNT_JSON
```

---

## Google Sheets Integration

The bot automatically:
- creates daily worksheets;
- appends race results;
- creates headers automatically.

Worksheet title format:

```text
14.09.2025
```

---

## Project Structure

```text
services/
├── formatter_service.py
├── google_sheet_service.py
├── ocr_service.py

bot.py
bot_local.py
requirements.txt
Dockerfile
```

---

## Notes

- Photos without valid VINRACE data are ignored.
- OCR quality depends on image quality.
- Google Vision API free tier limits may apply.

---

## License

MIT