from app.storage.memory_store import RoomMemoryStore
from app.storage.room_store import RoomMessage, RoomRecord, RoomStore
from app.services.room_validation import (
    validate_create_request,
    validate_join_request,
    validate_room_access,
)

room_store: RoomStore = RoomMemoryStore()


def configure_room_store(store: RoomStore) -> None:
    global room_store
    room_store = store


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


def room_exists(code: str) -> bool:
    return room_store.exists(code)


def create_room(code: str) -> RoomRecord:
    return room_store.create(code)


def get_room(code: str) -> RoomRecord | None:
    return room_store.get(code)


def get_room_messages(code: str) -> list[RoomMessage] | None:
    return room_store.get_messages(code)


def add_message(code: str, content: RoomMessage) -> bool:
    return room_store.add_message(code, content)


def add_member(code: str) -> bool:
    return room_store.add_member(code)


def remove_member(code: str) -> bool:
    return room_store.remove_member(code)


def list_rooms() -> list[str]:
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
