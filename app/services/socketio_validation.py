MAX_MESSAGE_LENGTH = 500

def validate_socket_session(room: object, name: object) -> tuple[str | None, str | None]:
    if not isinstance(room, str):
        return None, None
    if not isinstance(name, str):
        return None, None

    clean_room = room.strip()
    clean_name = name.strip()
    if not clean_room or not clean_name:
        return None, None

    return clean_room, clean_name


def validate_message_payload(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None

    raw_message = payload.get("data")
    if not isinstance(raw_message, str):
        return None

    message = raw_message.strip()
    if not message:
        return None
    if len(message) > MAX_MESSAGE_LENGTH:
        return None

    return message
