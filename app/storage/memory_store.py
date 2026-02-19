from app.storage.room_store import RoomMessage, RoomRecord, RoomStore


class RoomMemoryStore(RoomStore):
    def __init__(self) -> None:
        self._rooms: dict[str, RoomRecord] = {}

    def exists(self, code: str) -> bool:
        return code in self._rooms

    def create(self, code: str) -> RoomRecord:
        self._rooms[code] = {"members": 0, "messages": []}
        return self._rooms[code]

    def get(self, code: str) -> RoomRecord | None:
        return self._rooms.get(code)

    def get_messages(self, code: str) -> list[RoomMessage] | None:
        room = self.get(code)
        if not room:
            return None
        return room["messages"]

    def add_message(self, code: str, content: RoomMessage) -> bool:
        room = self.get(code)
        if not room:
            return False
        room["messages"].append(content)
        return True

    def add_member(self, code: str) -> bool:
        room = self.get(code)
        if not room:
            return False
        room["members"] += 1
        return True

    def remove_member(self, code: str) -> bool:
        room = self.get(code)
        if not room:
            return False
        room["members"] -= 1
        if room["members"] <= 0:
            del self._rooms[code]
        return True

    def room_codes(self) -> list[str]:
        return list(self._rooms.keys())
