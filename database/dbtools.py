import sqlite3
from config_data import CFG

class DBTools:
    def __init__(self, db_name=CFG.DATABASE_FOLDER_PATH):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS consultants (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                name TEXT,
                type TEXT DEFAULT 'consultant'
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                username TEXT,
                consultant_id INTEGER,
                FOREIGN KEY (consultant_id) REFERENCES consultants(id)
            )
        ''')
        self.conn.commit()

    def add_column(self):
        try:
            self.cursor.execute('ALTER TABLE consultants ADD COLUMN type TEXT DEFAULT "consultant"')
        except sqlite3.OperationalError:
            pass

    def add_consultant(self, user_id, name, consultant_type):
        self.cursor.execute('INSERT INTO consultants (user_id, name, type) VALUES (?, ?, ?)', (user_id, name, consultant_type))
        self.conn.commit()

    def get_consultants_by_type(self, consultant_type):
        self.cursor.execute('SELECT id, user_id, name FROM consultants WHERE type = ?', (consultant_type,))
        return self.cursor.fetchall()
    
    def get_consultant_by_db_id(self, db_id):
        self.cursor.execute('SELECT user_id, name FROM consultants WHERE id = ?', (db_id,))
        return self.cursor.fetchall()

    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()

    def add_user(self, user_id, username):
        self.cursor.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
        self.conn.commit()

    def set_user_consultant(self, user_id, consultant_id):
        self.cursor.execute('UPDATE users SET consultant_id = ? WHERE user_id = ?', (consultant_id, user_id))
        self.conn.commit()

    def get_consultant_name(self, consultant_id):
        self.cursor.execute('SELECT name FROM consultants WHERE user_id = ?', (consultant_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_consultant_types(self):
        self.cursor.execute('SELECT DISTINCT type FROM consultants')
        return [row[0] for row in self.cursor.fetchall()]

    def get_consultant_details(self, consultant_id):
        self.cursor.execute('SELECT user_id, name, type FROM consultants WHERE id = ?', (consultant_id,))
        return self.cursor.fetchone()
    
    def get_by_type(self, type):
        self.cursor.execute('SELECT * FROM consultants WHERE type = ?', (type,))
        return self.cursor.fetchall()

    def change_consultant(self, user_id, db_id, new_tg_id=None, new_name=None, new_type=None):
        allowed_user_ids = {688911314, 1038468423}
        if user_id not in allowed_user_ids:
            raise PermissionError("У вас нет прав для изменения данных специалиста.")
        
        if not self.get_consultant_by_db_id(db_id):
            raise ValueError("Специалист с таким ID не найден.")
        
        if new_tg_id is not None:
            self.cursor.execute('UPDATE consultants SET user_id = ? WHERE id = ?', (new_tg_id, db_id))
        if new_name is not None:
            self.cursor.execute('UPDATE consultants SET name = ? WHERE id = ?', (new_name, db_id))
        if new_type is not None:
            self.cursor.execute('UPDATE consultants SET type = ? WHERE id = ?', (new_type, db_id))

        self.conn.commit()

    def delete_consultant(self, user_id, consultant_id):
        self.cursor.execute('DELETE FROM consultants WHERE id = ?', (consultant_id,))
        self.cursor.execute('DELETE FROM users WHERE consultant_id = ?', (consultant_id,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()
