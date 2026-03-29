from app.storage.room_store import RoomMessage, RoomRecord, RoomStore
from app.services.room_validation import (
    validate_room_entry_code,
    validate_room_access,
)


class RoomService:
    def __init__(self, room_store: RoomStore) -> None:
        self._room_store = room_store

    def resolve_room_entry(
        self,
        name: str | None,
        code: str | None,
    ) -> tuple[str | None, str | None]:
        room_code = (code or "").strip()

        code_error = validate_room_entry_code(room_code)
        if code_error:
            return None, code_error

        if not self.room_exists(room_code):
            self.create_room(room_code)

        room_access_error = validate_room_access(room_code, name, self.room_exists)
        if room_access_error:
            return None, room_access_error

        return room_code, None

    def room_exists(self, code: str) -> bool:
        return self._room_store.exists(code)

    def create_room(self, code: str) -> RoomRecord:
        return self._room_store.create(code)

    def get_room(self, code: str) -> RoomRecord | None:
        return self._room_store.get(code)

    def get_room_messages(self, code: str) -> list[RoomMessage] | None:
        return self._room_store.get_messages(code)

    def get_message_count(self, code: str) -> int | None:
        return self._room_store.get_message_count(code)

    def get_member_count(self, code: str) -> int | None:
        return self._room_store.get_member_count(code)

    def add_message(self, code: str, content: RoomMessage) -> bool:
        return self._room_store.add_message(code, content)

    def add_member(self, code: str) -> bool:
        return self._room_store.add_member(code)

    def remove_member(self, code: str) -> bool:
        return self._room_store.remove_member(code)

    def list_rooms(self) -> list[str]:
        return self._room_store.room_codes()

    def build_room_view_context(
        self,
        name: str | None,
        room_code: str | None,
        rooms: list[str] | None = None,
    ) -> tuple[dict[str, object] | None, str | None]:
        room_access_error = validate_room_access(room_code, name, self.room_exists)
        if room_access_error:
            return None, room_access_error

        visible_rooms = rooms if rooms is not None else self.list_rooms()

        return {
            "code": room_code,
            "rooms": visible_rooms,
            "messages": self.get_room_messages(room_code),
            "member_count": self.get_member_count(room_code) or 0,
            "room_message_counts": {
                room: self.get_message_count(room) or 0 for room in visible_rooms
            },
        }, None
