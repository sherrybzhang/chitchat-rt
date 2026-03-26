from app.services.socketio_validation import MAX_MESSAGE_LENGTH, validate_message_payload, validate_socket_session


def test_validate_socket_session_success() -> None:
    room, name = validate_socket_session("  room-1  ", "  alice  ")
    assert room == "room-1"
    assert name == "alice"


def test_validate_socket_session_invalid() -> None:
    assert validate_socket_session(None, "alice") == (None, None)
    assert validate_socket_session("room", 123) == (None, None)
    assert validate_socket_session("   ", "alice") == (None, None)
    assert validate_socket_session("room", "   ") == (None, None)


def test_validate_message_payload_success() -> None:
    assert validate_message_payload({"data": "  hello  "}) == "hello"


def test_validate_message_payload_invalid() -> None:
    assert validate_message_payload(None) is None
    assert validate_message_payload({"data": None}) is None
    assert validate_message_payload({"data": ""}) is None
    assert validate_message_payload({"data": "   "}) is None
    assert validate_message_payload({"no_data": "hi"}) is None
    assert validate_message_payload({"data": "x" * (MAX_MESSAGE_LENGTH + 1)}) is None
