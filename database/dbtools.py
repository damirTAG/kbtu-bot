import aiosqlite
from config_data import CFG

class DBTools:
    def __init__(self, db_name=CFG.DATABASE_FOLDER_PATH):
        self.db_name = db_name

    async def init(self):
        self.connection = await aiosqlite.connect(self.db_name)
        self.cursor = await self.connection.cursor()
        await self.create_tables()

    async def create_tables(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS consultants (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    name TEXT,
                    type TEXT DEFAULT 'consultant'
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    username TEXT,
                    consultant_id INTEGER,
                    FOREIGN KEY (consultant_id) REFERENCES consultants(id)
                )
            ''')
            await db.commit()

    async def close_connection(self):
        await self.connection.close()

    async def backup_database(self, backup_path):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with aiosqlite.connect(backup_path) as backup_db:
                    await db.backup(backup_db)
        except Exception as e:
            raise Exception(f"Failed to backup database: {e}")

    async def add_column(self):
        async with aiosqlite.connect(self.db_name) as db:
            try:
                await db.execute('ALTER TABLE consultants ADD COLUMN type TEXT DEFAULT "consultant"')
            except aiosqlite.OperationalError:
                pass

    async def add_consultant(self, user_id, name, consultant_type):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('INSERT INTO consultants (user_id, name, type) VALUES (?, ?, ?)', (user_id, name, consultant_type))
            await db.commit()

    async def get_consultants_by_type(self, consultant_type):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT id, user_id, name FROM consultants WHERE type = ?', (consultant_type,))
            rows = await cursor.fetchall()
            return rows
    
    async def get_consultant_by_db_id(self, db_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT user_id, name FROM consultants WHERE id = ?', (db_id,))
            rows = await cursor.fetchall()
            return rows

    async def get_user(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            return row

    async def add_user(self, user_id, username):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
            await db.commit()

    async def set_user_consultant(self, user_id, consultant_id):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE users SET consultant_id = ? WHERE user_id = ?', (consultant_id, user_id))
            await db.commit()

    async def get_consultant_name(self, consultant_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT name FROM consultants WHERE user_id = ?', (consultant_id,))
            result = await cursor.fetchone()
            return result[0] if result else None

    async def get_consultant_types(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT DISTINCT type FROM consultants')
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def get_consultant_details(self, consultant_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT user_id, name, type FROM consultants WHERE id = ?', (consultant_id,))
            row = await cursor.fetchone()
            return row
    
    async def get_by_type(self, type):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM consultants WHERE type = ?', (type,))
            rows = await cursor.fetchall()
            return rows

    async def change_consultant(self, user_id, db_id, new_tg_id=None, new_name=None, new_type=None):
        allowed_user_ids = {688911314, 1038468423}
        if user_id not in allowed_user_ids:
            raise PermissionError("У вас нет прав для изменения данных специалиста.")
        
        if not await self.get_consultant_by_db_id(db_id):
            raise ValueError("Специалист с таким ID не найден.")
        
        async with aiosqlite.connect(self.db_name) as db:
            if new_tg_id is not None:
                await db.execute('UPDATE consultants SET user_id = ? WHERE id = ?', (new_tg_id, db_id))
            if new_name is not None:
                await db.execute('UPDATE consultants SET name = ? WHERE id = ?', (new_name, db_id))
            if new_type is not None:
                await db.execute('UPDATE consultants SET type = ? WHERE id = ?', (new_type, db_id))

            await db.commit()

    async def delete_consultant(self, user_id, consultant_id):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('DELETE FROM consultants WHERE id = ?', (consultant_id,))
            await db.execute('DELETE FROM users WHERE consultant_id = ?', (consultant_id,))
            await db.commit()
