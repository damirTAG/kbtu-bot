from aiogram import types
from aiogram import F
from config import dp, bot
from database.dbtools import DBTools
db_manager = DBTools()

@dp.message(F.content_type.in_({"photo", "document"}))
async def handle_files(message: types.Message):
    user_id = message.from_user.id
    user_record = db_manager.get_user(user_id)
    if not user_record or not user_record[3]:
        await message.reply("Пожалуйста, сначала выберите консультанта.")
        return
    if message.photo:
        photo_file_id = message.photo[-1].file_id
        await bot.send_photo(user_record[3], photo_file_id)
        await message.reply('Фото успешно передано консультанту')
    elif message.document:
        document_file_id = message.document.file_id
        await bot.send_document(user_record[3], document_file_id)
        await message.reply('Файл успешно передан консультанту')
    else:
        await message.reply("Пожалуйста, отправьте PDF или фото.")
