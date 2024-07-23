import asyncio
from aiologger import Logger
from handlers.commands import command_router
from handlers.callbacks import cb_router
from handlers.files import file_router
from config import bot, dp
from database.dbtools import DBTools

logger = Logger.with_default_handlers(name='bot-logs')

async def main():
    db_manager = DBTools()
    await db_manager.init()

    try:
        dp.include_routers(
            cb_router,
            command_router,
            file_router
        )
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await db_manager.close_connection()
        await logger.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
