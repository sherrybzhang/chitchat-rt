rooms = {}


def room_exists(code):
    return code in rooms


def create_room(code):
    rooms[code] = {"members": 0, "messages": []}
    return rooms[code]


def get_room(code):
    return rooms.get(code)


def get_room_messages(code):
    room = rooms.get(code)
    if not room:
        return None
    return room["messages"]


def add_message(code, content):
    room = rooms.get(code)
    if not room:
        return False
    room["messages"].append(content)
    return True


def add_member(code):
    room = rooms.get(code)
    if not room:
        return False
    room["members"] += 1
    return True


def remove_member(code):
    room = rooms.get(code)
    if not room:
        return False
    room["members"] -= 1
    if room["members"] <= 0:
        del rooms[code]
    return True
