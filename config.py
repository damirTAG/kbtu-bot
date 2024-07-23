from aiogram import Bot, Dispatcher
from config_data import CFG

API_TOKEN = CFG.TEST_BOT_TOKEN
bot = Bot(token=API_TOKEN)
dp = Dispatcher()