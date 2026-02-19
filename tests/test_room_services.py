import unittest

from app.services.room_services import RoomService
from app.services.room_validation import (
    ERR_NAME_REQUIRED,
    ERR_ROOM_CODE_REQUIRED,
    ERR_ROOM_EXISTS,
    ERR_ROOM_NOT_FOUND,
)
from app.storage.memory_store import RoomMemoryStore


class TestRoomServiceResolveEntry(unittest.TestCase):
    def setUp(self) -> None:
        self.service = RoomService(RoomMemoryStore())

    def test_create_room_success(self) -> None:
        room_code, error = self.service.resolve_room_entry(
            name="alice",
            code="abc",
            wants_join=False,
            wants_create=True,
        )
        self.assertEqual(room_code, "abc")
        self.assertIsNone(error)
        self.assertTrue(self.service.room_exists("abc"))

    def test_join_requires_code(self) -> None:
        room_code, error = self.service.resolve_room_entry(
            name="alice",
            code="",
            wants_join=True,
            wants_create=False,
        )
        self.assertIsNone(room_code)
        self.assertEqual(error, ERR_ROOM_CODE_REQUIRED)

    def test_join_nonexistent_room(self) -> None:
        room_code, error = self.service.resolve_room_entry(
            name="alice",
            code="missing",
            wants_join=True,
            wants_create=False,
        )
        self.assertIsNone(room_code)
        self.assertEqual(error, ERR_ROOM_NOT_FOUND)

    def test_create_existing_room_fails(self) -> None:
        self.service.create_room("abc")
        room_code, error = self.service.resolve_room_entry(
            name="alice",
            code="abc",
            wants_join=False,
            wants_create=True,
        )
        self.assertIsNone(room_code)
        self.assertEqual(error, ERR_ROOM_EXISTS)

    def test_missing_name_fails_room_access(self) -> None:
        self.service.create_room("abc")
        room_code, error = self.service.resolve_room_entry(
            name=None,
            code="abc",
            wants_join=True,
            wants_create=False,
        )
        self.assertIsNone(room_code)
        self.assertEqual(error, ERR_NAME_REQUIRED)


if __name__ == "__main__":
    unittest.main()
