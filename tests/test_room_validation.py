import unittest

from app.services.room_validation import (
    ERR_NAME_REQUIRED,
    ERR_ROOM_CODE_REQUIRED,
    ERR_ROOM_EXISTS,
    ERR_ROOM_NOT_FOUND,
    validate_create_request,
    validate_join_request,
    validate_name,
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

    def test_validate_join_request(self) -> None:
        def exists(code: str) -> bool:
            return code == "abc"

        self.assertEqual(validate_join_request(None, exists), ERR_ROOM_CODE_REQUIRED)
        self.assertEqual(validate_join_request("", exists), ERR_ROOM_CODE_REQUIRED)
        self.assertEqual(validate_join_request("missing", exists), ERR_ROOM_NOT_FOUND)
        self.assertIsNone(validate_join_request("abc", exists))

    def test_validate_create_request(self) -> None:
        def exists(code: str) -> bool:
            return code == "abc"

        self.assertEqual(validate_create_request(None, exists), ERR_ROOM_CODE_REQUIRED)
        self.assertEqual(validate_create_request("", exists), ERR_ROOM_CODE_REQUIRED)
        self.assertEqual(validate_create_request("abc", exists), ERR_ROOM_EXISTS)
        self.assertIsNone(validate_create_request("new-room", exists))


if __name__ == "__main__":
    unittest.main()
