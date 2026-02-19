from app.storage.memory_store import RoomMemoryStore

room_store = RoomMemoryStore()

def validate_join_request(code):
    if not code:
        return "Please enter a room code."
    if not room_exists(code):
        return "Room does not exist."
    return None


def validate_create_request(code):
    if not code:
        return "Please enter a room code."
    if room_exists(code):
        return "Room already exists. Click 'Join a Channel' to join. "
    return None


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
