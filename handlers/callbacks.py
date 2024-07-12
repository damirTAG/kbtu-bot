import logging
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import dp
from database.dbtools import DBTools

db_manager = DBTools()

@dp.callback_query(lambda c: c.data.startswith('role_'))
async def handle_role_selection(callback_query: CallbackQuery):
    role = callback_query.data.split('_')[1]
    consultants = db_manager.get_consultants_by_type(role)

    keyboard = InlineKeyboardBuilder()
    for consultant in consultants:
        keyboard.button(text=f"{consultant[2]}", callback_data=f"select_{role}_{consultant[1]}")
    keyboard.adjust(2)

    keyboard.button(text="Назад", callback_data="back_to_roles")

    await callback_query.message.edit_text("Выберите специалиста:", reply_markup=keyboard.as_markup())
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith('select_'))
async def handle_selection(callback_query: CallbackQuery):
    _, role, telegram_id = callback_query.data.split('_')
    consultant_telegram_id = int(telegram_id)
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username

    user_record = db_manager.get_user(user_id)
    if not user_record:
        db_manager.add_user(user_id, username)

    db_manager.set_user_consultant(user_id, consultant_telegram_id)
    consultant_name = db_manager.get_consultant_name(consultant_telegram_id)

    await callback_query.answer(f"Вы успешно выбрали {role} {consultant_name}")
    logging.info(f"Пользователь {user_id} выбрал {role} {consultant_name} (ID: {consultant_telegram_id}).")



@dp.callback_query(lambda c: c.data == 'back_to_roles')
async def handle_back_to_roles(callback_query: CallbackQuery):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Консультант", callback_data="role_consultant")
    keyboard.button(text="Технический секретарь", callback_data="role_tech")
    keyboard.adjust(1)
    await callback_query.message.edit_text("Выберите роль:", reply_markup=keyboard.as_markup())
    await callback_query.answer()