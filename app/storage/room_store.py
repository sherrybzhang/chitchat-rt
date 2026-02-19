from typing import Protocol, TypedDict


class RoomMessage(TypedDict):
    name: str
    message: str


class RoomRecord(TypedDict):
    members: int
    messages: list[RoomMessage]


class RoomStore(Protocol):
    def exists(self, code: str) -> bool:
        ...

    def create(self, code: str) -> RoomRecord:
        ...

    def get(self, code: str) -> RoomRecord | None:
        ...

    def get_messages(self, code: str) -> list[RoomMessage] | None:
        ...

    def add_message(self, code: str, content: RoomMessage) -> bool:
        ...

    def add_member(self, code: str) -> bool:
        ...

    def remove_member(self, code: str) -> bool:
        ...

    def room_codes(self) -> list[str]:
        ...
