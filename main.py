import asyncio
import logging
import handlers.commands
import handlers.callbacks
import handlers.files
from config import bot, dp
from database.dbtools import DBTools
from aiocron import crontab
from datetime import datetime

logging.basicConfig(level=logging.INFO)

async def backup_database():
    try:
        print('w')
        db_manager = DBTools()
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"consultants_{current_time}.db"
        backup_path = f"database/backup/{backup_filename}"

        # backuping
        db_manager.backup_database(backup_path)

        logging.info(f"Backup created: {backup_path}")

        db_manager.close_connection()
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")

async def main():
    # settings for backuppp
    crontab('0 0 * * *', func=backup_database, start=True)

    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        db_manager = DBTools()
        db_manager.close_connection()

if __name__ == "__main__":
    asyncio.run(main())
