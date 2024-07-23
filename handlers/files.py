from aiogram import types, F, Router
from config import bot
from database.dbtools import DBTools
import asyncio
import logging
from aiogram.exceptions import TelegramNetworkError, TelegramAPIError

db_manager = DBTools()
file_router = Router()

@file_router.message(F.content_type.in_({"photo", "document"}))
async def handle_files(message: types.Message):
    try:
        await db_manager.init()
    except Exception as e:
        logging.exception("Failed to initialize the database connection", exc_info=e)
        await message.reply("Произошла ошибка при подключении к базе данных. Попробуйте позже.")
        return

    user_id = message.from_user.id

    try:
        user_record = await db_manager.get_user(user_id)
    except Exception as e:
        logging.exception("Failed to fetch user record from the database", exc_info=e)
        await message.reply("Произошла ошибка при получении данных пользователя. Попробуйте позже.")
        return

    if not user_record or not user_record[3]:
        await message.reply("Пожалуйста, сначала выберите консультанта.")
        return

    files = []
    if message.photo:
        files = message.photo
        send_func = bot.send_photo
    elif message.document:
        files = [message.document]
        send_func = bot.send_document

    if not files:
        await message.reply("Пожалуйста, отправьте PDF или фото.")
        return

    successful_files = []
    failed_files = []

    for file in files:
        file_id = file.file_id
        retries = 0
        max_retries = 5
        retry_delay = 1

        while retries < max_retries:
            try:
                await send_func(user_record[3], file_id)
                successful_files.append(file.file_unique_id)
                break
            except TelegramNetworkError as e:
                retries += 1
                logging.error(f"TelegramNetworkError: {e}. Retrying in {retry_delay} seconds... (attempt {retries}/{max_retries})")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            except TelegramAPIError as e:
                logging.error(f"TelegramAPIError: {e}")
                failed_files.append(file.file_unique_id)
                break
            except Exception as e:
                logging.exception("An unexpected error occurred while sending the file", exc_info=e)
                failed_files.append(file.file_unique_id)
                break
        else:
            failed_files.append(file.file_unique_id)

    if successful_files:
        await message.reply('Файлы успешно переданы консультанту')

    if failed_files:
        await message.reply("Некоторые файлы не удалось отправить после нескольких попыток. Пожалуйста, попробуйте позже.")
