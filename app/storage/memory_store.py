class RoomMemoryStore:
    def __init__(self):
        self._rooms = {}

    def exists(self, code):
        return code in self._rooms

    def create(self, code):
        self._rooms[code] = {"members": 0, "messages": []}
        return self._rooms[code]

    def get(self, code):
        return self._rooms.get(code)

    def get_messages(self, code):
        room = self.get(code)
        if not room:
            return None
        return room["messages"]

    def add_message(self, code, content):
        room = self.get(code)
        if not room:
            return False
        room["messages"].append(content)
        return True

    def add_member(self, code):
        room = self.get(code)
        if not room:
            return False
        room["members"] += 1
        return True

    def remove_member(self, code):
        room = self.get(code)
        if not room:
            return False
        room["members"] -= 1
        if room["members"] <= 0:
            del self._rooms[code]
        return True

    def room_codes(self):
        return list(self._rooms.keys())
