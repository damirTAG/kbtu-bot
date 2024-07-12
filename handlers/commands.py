import logging
from aiogram import types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import dp
from database.dbtools import DBTools
db_manager = DBTools()

allowed_user_ids = {688911314, 1038468423}

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    logging.info("Received /start command from user %s", message.from_user.id)
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Консультант", callback_data="role_consultant")
    keyboard.button(text="Технический секретарь", callback_data="role_tech")
    keyboard.adjust(1)
    await message.reply("Выберите роль:", reply_markup=keyboard.as_markup())

# команда чтоб добавить нового консультанта/специалиста в бд
# ща тут буду чисто CRUD операции для добавления/просмотра/изменения/удаления объектов в бд

@dp.message(Command("add"))
async def add_consultant_command(message: types.Message):
    allowed_user_ids = {688911314, 1038468423}

    if message.from_user.id not in allowed_user_ids:
        await message.reply("У вас нет доступа к этой команде.")
        return

    try:
        _, user_id, name, consultant_type = message.text.split(maxsplit=3)
        db_manager.add_consultant(user_id, name, consultant_type)
        await message.reply(f"{consultant_type.capitalize()} {name} успешно добавлен.")
        logging.info(f"{consultant_type.capitalize()} {name} успешно добавлен.")
    except ValueError:
        await message.reply("Используйте команду /add <tg_id> <имя> <type> для добавления специалиста.")

# UPDATE
@dp.message(Command("change"))
async def change_consultant_command(message: types.Message):
    allowed_user_ids = {688911314, 1038468423}

    if message.from_user.id not in allowed_user_ids:
        await message.reply("У вас нет доступа к этой команде.")
        return

    try:
        args = message.text.split(maxsplit=1)[1]
        db_id = None
        tg_id = None
        name = None
        consultant_type = None

        for arg in args.split():
            if arg.startswith('id='):
                db_id = int(arg[3:])
            elif arg.startswith('tg='):
                tg_id = int(arg[3:])
            elif arg.startswith('name='):
                name = arg[5:]
            elif arg.startswith('type='):
                consultant_type = arg[5:]

        if db_id is None:
            await message.reply("Укажите ID специалиста с помощью id={id}.")
            return
        
        db_manager.change_consultant(
            user_id=message.from_user.id,
            db_id=db_id,
            new_tg_id=tg_id,
            new_name=name,
            new_type=consultant_type
        )
        await message.reply(f"Данные специалиста с ID {db_id} обновлены.")
        logging.info(f"Данные специалиста с ID {db_id} обновлены пользователем {message.from_user.id}.")

    except ValueError:
        await message.reply("Используйте команду /change id={id} tg={new_tg_id} name={new_name} type={new_type} для изменения данных специалиста.")
    except PermissionError as e:
        await message.reply(str(e))

# DELETE
@dp.message(Command("delete"))
async def delete_cons(message: types.Message):
    allowed_user_ids = {688911314, 1038468423}

    if message.from_user.id not in allowed_user_ids:
        await message.reply("У вас нет доступа к этой команде.")
        return

    try:
        _, consultant_id = message.text.split(maxsplit=1)
        consultant_id = int(consultant_id)
        user_id = message.from_user.id

        db_manager.delete_consultant(user_id, consultant_id)
        await message.reply(f"Специалист с ID {consultant_id} успешно удален.")
        logging.info(
            f"Специалист с ID {consultant_id} успешно удален пользователем {user_id}.")
    except ValueError:
        await message.reply("Используйте команду /delete <id> для удаления специалиста.")
    except PermissionError as e:
        await message.reply(str(e))


@dp.message(Command("list"))
async def list_command(message: types.Message):
    allowed_user_ids = {688911314, 1038468423}

    if message.from_user.id not in allowed_user_ids:
        await message.reply("У вас нет доступа к этой команде.")
        return

    try:
        _, consultant_type = message.text.split(maxsplit=1)
        consultants = db_manager.get_by_type(consultant_type)
        if consultants:
            response = "\n".join([f"ID: {c[0]}, Name: {c[2]}" for c in consultants])
        else:
            response = "Нет специалистов с указанным типом."
        await message.reply(response)
        logging.info(f"Список {consultant_type} специалистов отправлен пользователю {message.from_user.id}.")
    except ValueError:
        await message.reply("Используйте команду /list <type> для получения списка специалистов.")


@dp.message(Command("list_types"))
async def list_types_command(message: types.Message):
    allowed_user_ids = {688911314, 1038468423}

    if message.from_user.id not in allowed_user_ids:
        await message.reply("У вас нет доступа к этой команде.")
        return

    types = db_manager.get_consultant_types()
    response = "\n".join(types) if types else "Типы специалистов не найдены."
    await message.reply(f"Доступные типы специалистов:\n{response}")
    logging.info(f"Список типов специалистов отправлен пользователю {message.from_user.id}.")


@dp.message(Command("show_details"))
async def show_details_command(message: types.Message):
    allowed_user_ids = {688911314, 1038468423}

    if message.from_user.id not in allowed_user_ids:
        await message.reply("У вас нет доступа к этой команде.")
        return

    try:
        _, consultant_id = message.text.split(maxsplit=1)
        consultant_id = int(consultant_id)
        details = db_manager.get_consultant_details(consultant_id)
        if details:
            user_id, name, consultant_type = details
            response = f"ID: {consultant_id}\nUser ID: {user_id}\nName: {name}\nType: {consultant_type}"
        else:
            response = "Специалист не найден."
        await message.reply(response)
        logging.info(f"Детали специалиста с ID {consultant_id} отправлены пользователю {message.from_user.id}.")
    except ValueError:
        await message.reply("Используйте команду /show_details <id> для получения информации о специалисте.")
