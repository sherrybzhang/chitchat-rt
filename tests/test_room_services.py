import unittest

from app.services.room_services import RoomService
from app.services.room_validation import (
    ERR_NAME_REQUIRED,
    ERR_ROOM_CODE_REQUIRED,
)
from app.storage.memory_store import RoomMemoryStore


class TestRoomServiceResolveEntry(unittest.TestCase):
    def setUp(self) -> None:
        self.service = RoomService(RoomMemoryStore())

    def test_creates_missing_room_when_entering(self) -> None:
        room_code, error = self.service.resolve_room_entry(name="alice", code="abc")
        self.assertEqual(room_code, "abc")
        self.assertIsNone(error)
        self.assertTrue(self.service.room_exists("abc"))

    def test_enter_requires_code(self) -> None:
        room_code, error = self.service.resolve_room_entry(name="alice", code="")
        self.assertIsNone(room_code)
        self.assertEqual(error, ERR_ROOM_CODE_REQUIRED)

    def test_enters_existing_room_without_creating_duplicate(self) -> None:
        self.service.create_room("abc")
        room_code, error = self.service.resolve_room_entry(name="alice", code="abc")
        self.assertEqual(room_code, "abc")
        self.assertIsNone(error)
        self.assertEqual(self.service.list_rooms(), ["abc"])

    def test_missing_name_fails_room_access(self) -> None:
        self.service.create_room("abc")
        room_code, error = self.service.resolve_room_entry(name=None, code="abc")
        self.assertIsNone(room_code)
        self.assertEqual(error, ERR_NAME_REQUIRED)


if __name__ == "__main__":
    unittest.main()
