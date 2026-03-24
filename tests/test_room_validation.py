import unittest

from app.services.room_validation import (
    ERR_NAME_REQUIRED,
    ERR_ROOM_CODE_REQUIRED,
    ERR_ROOM_NOT_FOUND,
    validate_name,
    validate_room_entry_code,
    validate_room_access,
)


class TestRoomValidation(unittest.TestCase):
    def test_validate_name(self) -> None:
        self.assertEqual(validate_name(None), ERR_NAME_REQUIRED)
        self.assertEqual(validate_name(""), ERR_NAME_REQUIRED)
        self.assertIsNone(validate_name("alice"))

    def test_validate_room_access(self) -> None:
        def exists(code: str) -> bool:
            return code == "abc"

        self.assertEqual(validate_room_access("abc", None, exists), ERR_NAME_REQUIRED)
        self.assertEqual(validate_room_access(None, "alice", exists), ERR_ROOM_NOT_FOUND)
        self.assertEqual(validate_room_access("missing", "alice", exists), ERR_ROOM_NOT_FOUND)
        self.assertIsNone(validate_room_access("abc", "alice", exists))

    def test_validate_room_entry_code(self) -> None:
        self.assertEqual(validate_room_entry_code(None), ERR_ROOM_CODE_REQUIRED)
        self.assertEqual(validate_room_entry_code(""), ERR_ROOM_CODE_REQUIRED)
        self.assertIsNone(validate_room_entry_code("abc"))


if __name__ == "__main__":
    unittest.main()
