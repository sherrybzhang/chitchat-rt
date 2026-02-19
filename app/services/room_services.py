from app.storage.memory_store import RoomMemoryStore

room_store = RoomMemoryStore()

ERR_NAME_REQUIRED = "* Please enter a name"
ERR_ROOM_CODE_REQUIRED = "Please enter a room code."
ERR_ROOM_EXISTS = "Room already exists. Click 'Join a Channel' to join. "
ERR_ROOM_NOT_FOUND = "Room does not exist."


def validate_name(name):
    if not name:
        return ERR_NAME_REQUIRED
    return None


def validate_room_access(room_code, name):
    if not name:
        return ERR_NAME_REQUIRED
    if not room_code:
        return ERR_ROOM_NOT_FOUND
    if not room_exists(room_code):
        return ERR_ROOM_NOT_FOUND
    return None

def validate_join_request(code):
    if not code:
        return ERR_ROOM_CODE_REQUIRED
    if not room_exists(code):
        return ERR_ROOM_NOT_FOUND
    return None


def validate_create_request(code):
    if not code:
        return ERR_ROOM_CODE_REQUIRED
    if room_exists(code):
        return ERR_ROOM_EXISTS
    return None


def resolve_room_entry(name, code, wants_join, wants_create):
    room_code = (code or "").strip()

    if wants_join:
        join_error = validate_join_request(room_code)
        if join_error:
            return None, join_error

    if wants_create:
        create_error = validate_create_request(room_code)
        if create_error:
            return None, create_error
        create_room(room_code)

    if not room_exists(room_code):
        return None, validate_join_request(room_code)

    room_access_error = validate_room_access(room_code, name)
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
    room_access_error = validate_room_access(room_code, name)
    if room_access_error:
        return None, room_access_error

    return {
        "code": room_code,
        "rooms": list_rooms(),
        "messages": get_room_messages(room_code),
    }, None
