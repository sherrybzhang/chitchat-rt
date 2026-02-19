from app.storage.memory_store import RoomMemoryStore
from app.services.room_validation import (
    validate_create_request,
    validate_join_request,
    validate_room_access,
)

room_store = RoomMemoryStore()


def resolve_room_entry(name, code, wants_join, wants_create):
    room_code = (code or "").strip()

    if wants_join:
        join_error = validate_join_request(room_code, room_exists)
        if join_error:
            return None, join_error

    if wants_create:
        create_error = validate_create_request(room_code, room_exists)
        if create_error:
            return None, create_error
        create_room(room_code)

    if not room_exists(room_code):
        return None, validate_join_request(room_code, room_exists)

    room_access_error = validate_room_access(room_code, name, room_exists)
    if room_access_error:
        return None, room_access_error

    return room_code, None


def room_exists(code):
    return room_store.exists(code)


def create_room(code):
    return room_store.create(code)


def get_room(code):
    return room_store.get(code)


def get_room_messages(code):
    return room_store.get_messages(code)


def add_message(code, content):
    return room_store.add_message(code, content)


def add_member(code):
    return room_store.add_member(code)


def remove_member(code):
    return room_store.remove_member(code)


def list_rooms():
    return room_store.room_codes()


def build_room_view_context(name, room_code):
    room_access_error = validate_room_access(room_code, name, room_exists)
    if room_access_error:
        return None, room_access_error

    return {
        "code": room_code,
        "rooms": list_rooms(),
        "messages": get_room_messages(room_code),
    }, None
