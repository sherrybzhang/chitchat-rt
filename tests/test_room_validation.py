from app.services.room_validation import (
    ERR_NAME_REQUIRED,
    ERR_ROOM_CODE_REQUIRED,
    ERR_ROOM_NOT_FOUND,
    validate_name,
    validate_room_entry_code,
    validate_room_access,
)


def test_validate_name() -> None:
    assert validate_name(None) == ERR_NAME_REQUIRED
    assert validate_name("") == ERR_NAME_REQUIRED
    assert validate_name("alice") is None


def test_validate_room_access() -> None:
    def exists(code: str) -> bool:
        return code == "abc"

    assert validate_room_access("abc", None, exists) == ERR_NAME_REQUIRED
    assert validate_room_access(None, "alice", exists) == ERR_ROOM_NOT_FOUND
    assert validate_room_access("missing", "alice", exists) == ERR_ROOM_NOT_FOUND
    assert validate_room_access("abc", "alice", exists) is None


def test_validate_room_entry_code() -> None:
    assert validate_room_entry_code(None) == ERR_ROOM_CODE_REQUIRED
    assert validate_room_entry_code("") == ERR_ROOM_CODE_REQUIRED
    assert validate_room_entry_code("abc") is None
