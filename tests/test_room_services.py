from app.services.room_services import RoomService
from app.services.room_validation import (
    ERR_NAME_REQUIRED,
    ERR_ROOM_CODE_REQUIRED,
)
from app.storage.memory_store import RoomMemoryStore

import pytest


@pytest.fixture
def service() -> RoomService:
    return RoomService(RoomMemoryStore())


def test_creates_missing_room_when_entering(service: RoomService) -> None:
    room_code, error = service.resolve_room_entry(name="alice", code="abc")
    assert room_code == "abc"
    assert error is None
    assert service.room_exists("abc")


def test_enter_requires_code(service: RoomService) -> None:
    room_code, error = service.resolve_room_entry(name="alice", code="")
    assert room_code is None
    assert error == ERR_ROOM_CODE_REQUIRED


def test_enters_existing_room_without_creating_duplicate(service: RoomService) -> None:
    service.create_room("abc")
    room_code, error = service.resolve_room_entry(name="alice", code="abc")
    assert room_code == "abc"
    assert error is None
    assert service.list_rooms() == ["abc"]


def test_missing_name_fails_room_access(service: RoomService) -> None:
    service.create_room("abc")
    room_code, error = service.resolve_room_entry(name=None, code="abc")
    assert room_code is None
    assert error == ERR_NAME_REQUIRED
