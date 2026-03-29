from pathlib import Path

from app.storage.sqlite_store import SQLiteRoomStore


def test_sqlite_store_persists_rooms_and_messages(tmp_path: Path) -> None:
    database_path = tmp_path / "chat.db"

    store = SQLiteRoomStore(database_path)
    store.create("lobby")
    store.add_message("lobby", {"name": "alice", "message": "hello"})

    reloaded_store = SQLiteRoomStore(database_path)

    assert reloaded_store.exists("lobby") is True
    assert reloaded_store.room_codes() == ["lobby"]
    assert reloaded_store.get_messages("lobby") == [{"name": "alice", "message": "hello"}]
    assert reloaded_store.get_member_count("lobby") == 0


def test_sqlite_store_keeps_room_after_last_member_leaves(tmp_path: Path) -> None:
    database_path = tmp_path / "chat.db"
    store = SQLiteRoomStore(database_path)
    store.create("lobby")

    assert store.add_member("lobby") is True
    assert store.remove_member("lobby") is True
    assert store.exists("lobby") is True
    assert store.get_member_count("lobby") == 0
