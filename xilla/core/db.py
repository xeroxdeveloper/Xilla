import sqlite3
import os
import logging

class XillaDB:
    """Легкая обертка SQLite3 (Только для модулей, которым это нужно)"""
    def __init__(self):
        self.logger = logging.getLogger("XillaDB")
        db_path = os.path.join(os.getcwd(), "database", "xilla.db")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.logger.info("SQLite3 DB инициализирована")

    def execute(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor
        except Exception as e:
            self.logger.error(f"SQL Error: {e}")
            return None

    def fetchall(self, query, params=()):
        cur = self.execute(query, params)
        return cur.fetchall() if cur else []

    def fetchone(self, query, params=()):
        cur = self.execute(query, params)
        return cur.fetchone() if cur else None
