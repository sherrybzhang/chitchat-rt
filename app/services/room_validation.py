ERR_NAME_REQUIRED = "Please enter a name."
ERR_ROOM_CODE_REQUIRED = "Please enter a room code."
ERR_ROOM_EXISTS = "Room already exists. Click 'Join a Channel' to join."
ERR_ROOM_NOT_FOUND = "Room does not exist."


def validate_name(name):
    if not name:
        return ERR_NAME_REQUIRED
    return None


def validate_room_access(room_code, name, room_exists_fn):
    if not name:
        return ERR_NAME_REQUIRED
    if not room_code:
        return ERR_ROOM_NOT_FOUND
    if not room_exists_fn(room_code):
        return ERR_ROOM_NOT_FOUND
    return None


def validate_join_request(code, room_exists_fn):
    if not code:
        return ERR_ROOM_CODE_REQUIRED
    if not room_exists_fn(code):
        return ERR_ROOM_NOT_FOUND
    return None


def validate_create_request(code, room_exists_fn):
    if not code:
        return ERR_ROOM_CODE_REQUIRED
    if room_exists_fn(code):
        return ERR_ROOM_EXISTS
    return None
