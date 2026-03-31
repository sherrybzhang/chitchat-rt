from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from app.storage.room_store import RoomMessage, RoomRecord, RoomStore


class SQLiteRoomStore(RoomStore):
    def __init__(self, database_path: str | Path) -> None:
        self._database_path = str(database_path)
        self._member_counts: dict[str, int] = {}
        self._member_counts_lock = threading.Lock()
        self._schema_lock = threading.Lock()

        if self._database_path != ":memory:":
            Path(self._database_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

        self._initialize_database()

    def _open_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize_database(self) -> None:
        with self._schema_lock:
            with self._open_connection() as connection:
                self._ensure_schema(connection)

    def _ensure_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_code TEXT NOT NULL,
                name TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_code) REFERENCES rooms(code) ON DELETE CASCADE
            )
            """
        )

    def _connect(self) -> sqlite3.Connection:
        connection = self._open_connection()
        with self._schema_lock:
            self._ensure_schema(connection)
        return connection

    def exists(self, code: str) -> bool:
        with self._connect() as connection:
            row = connection.execute("SELECT 1 FROM rooms WHERE code = ?", (code,)).fetchone()
        return row is not None

    def create(self, code: str) -> RoomRecord:
        with self._connect() as connection:
            connection.execute("INSERT OR IGNORE INTO rooms (code) VALUES (?)", (code,))

        room = self.get(code)
        if room is None:
            raise RuntimeError(f"Failed to create or load room {code!r}")
        return room

    def get(self, code: str) -> RoomRecord | None:
        if not self.exists(code):
            return None

        messages = self.get_messages(code)
        member_count = self.get_member_count(code)
        return {
            "members": member_count or 0,
            "messages": messages or [],
        }

    def get_messages(self, code: str) -> list[RoomMessage] | None:
        if not self.exists(code):
            return None

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT name, message
                FROM messages
                WHERE room_code = ?
                ORDER BY id ASC
                """,
                (code,),
            ).fetchall()

        return [{"name": row["name"], "message": row["message"]} for row in rows]

    def get_message_count(self, code: str) -> int | None:
        if not self.exists(code):
            return None

        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM messages WHERE room_code = ?",
                (code,),
            ).fetchone()

        return int(row["count"]) if row is not None else 0

    def get_member_count(self, code: str) -> int | None:
        if not self.exists(code):
            return None

        with self._member_counts_lock:
            return self._member_counts.get(code, 0)

    def add_message(self, code: str, content: RoomMessage) -> bool:
        if not self.exists(code):
            return False

        with self._connect() as connection:
            connection.execute(
                "INSERT INTO messages (room_code, name, message) VALUES (?, ?, ?)",
                (code, content["name"], content["message"]),
            )
        return True

    def add_member(self, code: str) -> bool:
        if not self.exists(code):
            return False

        with self._member_counts_lock:
            self._member_counts[code] = self._member_counts.get(code, 0) + 1
        return True

    def remove_member(self, code: str) -> bool:
        if not self.exists(code):
            return False

        with self._member_counts_lock:
            current_count = self._member_counts.get(code, 0)
            if current_count <= 1:
                self._member_counts.pop(code, None)
            else:
                self._member_counts[code] = current_count - 1
        return True

    def room_codes(self) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT code
                FROM rooms
                ORDER BY id ASC
                """
            ).fetchall()

        return [row["code"] for row in rows]
