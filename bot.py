import asyncio
import traceback
import json
import os
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from services.ocr_service import recognize_text
from logging.handlers import RotatingFileHandler

from services.formatter_service import (
    parse_race_result,
    format_race_result,
    is_valid_race_result,
)

from services.google_sheet_service import (
    append_result_to_sheet,
)

load_dotenv()

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("faxo_bot")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

file_handler = RotatingFileHandler(
    "logs/bot.log",
    maxBytes=1_000_000,
    backupCount=5,
    encoding="utf-8"
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

TOKEN = os.getenv("BOT_TOKEN")
ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD")

AUTHORIZED_USERS_FILE = "data/authorized_users.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()


def load_authorized_users() -> set[int]:
    if not os.path.exists(AUTHORIZED_USERS_FILE):
        return set()

    with open(AUTHORIZED_USERS_FILE, "r", encoding="utf-8") as file:
        return set(json.load(file))


def save_authorized_user(user_id: int):
    os.makedirs("data", exist_ok=True)

    users = load_authorized_users()
    users.add(user_id)

    with open(AUTHORIZED_USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(list(users), file)


def is_authorized(user_id: int) -> bool:
    return user_id in load_authorized_users()


@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id

    logger.info(f"Start by {user_id}")

    if is_authorized(user_id):
        await message.answer(
            "✅ Ви вже авторизовані.\n"
            "Просто надішліть фото."
        )
        return

    await message.answer(
        "🔐 Введіть пароль для доступу."
    )


@dp.message(F.text)
async def password_handler(message: Message):
    user_id = message.from_user.id

    if is_authorized(user_id):
        return

    user_password = message.text.strip()

    if user_password == ACCESS_PASSWORD:
        save_authorized_user(user_id)

        logger.info(f"Success password by {user_id}")

        await message.answer(
            "✅ Доступ надано.\n"
            "Тепер можете надсилати фото."
        )
    else:
        logger.info(f"Failed password by {user_id}")
        await message.answer(
            "❌ Невірний пароль."
        )

@dp.message(F.photo)
async def photo_handler(message: Message):
    user_id = message.from_user.id
    logger.info(f"Received image from {user_id}")

    try:
        if not is_authorized(user_id):
            logger.warning(f"Unauthorized photo attempt from user_id={user_id}")
            await message.answer(
                "⛔ У вас немає дозволу до публікації.\n"
                "Напишіть /start та введіть пароль."
            )
            return

        logger.info("Start processing photo")
        await message.answer("⏳ Обробляю фото...")

        photo = message.photo[-1]

        file = await bot.get_file(photo.file_id)
        file_data = await bot.download_file(file.file_path)

        image_bytes = file_data.read()

        text = recognize_text(image_bytes)

        if not text:
            logger.warning(f"Empty text")
            await message.answer(
                "❌ Помилка: текст на фото не знайдено."
            )
            return

        result = parse_race_result(text)

        if not is_valid_race_result(result):
            logger.warning(f"Not valid data={text}")
            await message.answer(
                "❌ Не знайдено коректні дані заїзду на фото.\n"
                "Публікацію скасовано."
            )
            return

        formatted_text = format_race_result(result)



        await bot.send_message(
            chat_id=os.getenv("CHANNEL_ID"),
            text=formatted_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

        await message.answer("✅ Опубліковано")

        append_result_to_sheet(result)

        logger.info(
            f"Published race result: {formatted_text}"
        )
    except Exception as e:
        logger.exception("Photo processing failed str")
        print("\n========== ERROR ==========")
        traceback.print_exc()
        print("========== ERROR ==========\n")

        await message.answer(
            f"❌ Помилка:\n{str(e)}"
        )

async def main():
    print("Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())