import os
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional, Tuple

DEFAULT_DB = os.path.expanduser("~/.clip_history.db")


class Storage:
    def __init__(self, path: str = DEFAULT_DB):
        self.path = path
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        c = self._conn.cursor()
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS clips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
        )
        self._conn.commit()

    def add(self, text: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        c = self._conn.cursor()
        c.execute("INSERT INTO clips (text, created_at) VALUES (?, ?)", (text, now))
        self._conn.commit()
        return c.lastrowid

    def list(self, limit: int = 100) -> List[Tuple[int, str, str]]:
        c = self._conn.cursor()
        c.execute(
            "SELECT id, text, created_at FROM clips ORDER BY id DESC LIMIT ?", (limit,)
        )
        return c.fetchall()

    def get(self, clip_id: int) -> Optional[Tuple[int, str, str]]:
        c = self._conn.cursor()
        c.execute("SELECT id, text, created_at FROM clips WHERE id = ?", (clip_id,))
        return c.fetchone()

    def delete(self, clip_id: int) -> None:
        c = self._conn.cursor()
        c.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
        self._conn.commit()

    def clear(self) -> None:
        c = self._conn.cursor()
        c.execute("DELETE FROM clips")
        self._conn.commit()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass

