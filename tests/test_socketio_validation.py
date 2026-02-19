import unittest

from app.services.socketio_validation import MAX_MESSAGE_LENGTH, validate_message_payload, validate_socket_session


class TestSocketValidation(unittest.TestCase):
    def test_validate_socket_session_success(self) -> None:
        room, name = validate_socket_session("  room-1  ", "  alice  ")
        self.assertEqual(room, "room-1")
        self.assertEqual(name, "alice")

    def test_validate_socket_session_invalid(self) -> None:
        self.assertEqual(validate_socket_session(None, "alice"), (None, None))
        self.assertEqual(validate_socket_session("room", 123), (None, None))
        self.assertEqual(validate_socket_session("   ", "alice"), (None, None))
        self.assertEqual(validate_socket_session("room", "   "), (None, None))

    def test_validate_message_payload_success(self) -> None:
        self.assertEqual(validate_message_payload({"data": "  hello  "}), "hello")

    def test_validate_message_payload_invalid(self) -> None:
        self.assertIsNone(validate_message_payload(None))
        self.assertIsNone(validate_message_payload({"data": None}))
        self.assertIsNone(validate_message_payload({"data": ""}))
        self.assertIsNone(validate_message_payload({"data": "   "}))
        self.assertIsNone(validate_message_payload({"no_data": "hi"}))
        self.assertIsNone(validate_message_payload({"data": "x" * (MAX_MESSAGE_LENGTH + 1)}))


if __name__ == "__main__":
    unittest.main()
