import logging
import threading

from flask import request, session
from flask_socketio import join_room, leave_room, send

from app import socketio
from app.services.room_services import RoomService
from app.services.socketio_validation import validate_message_payload, validate_socket_session

logger = logging.getLogger(__name__)
_connection_registry_lock = threading.Lock()
_connection_registry: dict[str, dict[str, object]] = {}


def emit_presence_update(room_service: RoomService, room: str) -> None:
    member_count = room_service.get_member_count(room)
    if member_count is None:
        return

    socketio.emit("presence", {"count": member_count}, to=room)


def get_session_joined_rooms(room_service: RoomService, current_room: str) -> list[str]:
    raw_rooms = session.get("rooms", [])
    joined_rooms: list[str] = []

    if isinstance(raw_rooms, list):
        for room in raw_rooms:
            if not isinstance(room, str):
                continue
            if not room_service.room_exists(room):
                continue
            if room not in joined_rooms:
                joined_rooms.append(room)

    if current_room not in joined_rooms and room_service.room_exists(current_room):
        joined_rooms.append(current_room)

    return joined_rooms


def register_connection(room_service: RoomService, current_room: str) -> None:
    with _connection_registry_lock:
        _connection_registry[request.sid] = {
            "current_room": current_room,
            "joined_rooms": get_session_joined_rooms(room_service, current_room),
        }


def unregister_connection() -> None:
    with _connection_registry_lock:
        _connection_registry.pop(request.sid, None)


def get_registered_room() -> str | None:
    with _connection_registry_lock:
        connection_state = _connection_registry.get(request.sid)

    current_room = connection_state.get("current_room") if isinstance(connection_state, dict) else None
    return current_room if isinstance(current_room, str) else None


def emit_unread_update(room: str) -> None:
    with _connection_registry_lock:
        target_sids = [
            sid
            for sid, state in _connection_registry.items()
            if room in state["joined_rooms"] and state["current_room"] != room
        ]

    for sid in target_sids:
        socketio.emit("unread_update", {"room": room, "increment": 1}, to=sid)


def register_socketio_handlers(room_service: RoomService) -> None:
    @socketio.on("message")
    def message(data: object) -> None:
        room, name = validate_socket_session(session.get("room"), session.get("name"))
        if not room or not name:
            return
        if not room_service.room_exists(room):
            return

        message_text = validate_message_payload(data)
        if message_text is None:
            return

        content = {
            "name": name,
            "message": message_text,
        }
        send(content, to=room)
        room_service.add_message(room, content)
        emit_unread_update(room)
        logger.info("%s said: %s", name, message_text)

    @socketio.on("connect")
    def connect(auth: object | None) -> None:
        if auth is not None and not isinstance(auth, dict):
            return

        room, name = validate_socket_session(session.get("room"), session.get("name"))
        if not room or not name:
            return
        if not room_service.room_exists(room):
            leave_room(room)
            return

        join_room(room)
        register_connection(room_service, room)
        room_service.add_member(room)
        emit_presence_update(room_service, room)
        logger.info("%s joined room %s", name, room)

    @socketio.on("announce_join")
    def announce_join() -> None:
        room, name = validate_socket_session(session.get("room"), session.get("name"))
        if not room or not name:
            return
        if not room_service.room_exists(room):
            return

        send({"name": name, "message": "has entered the room"}, to=room)

    @socketio.on("disconnect")
    def disconnect() -> None:
        room = get_registered_room()
        name = session.get("name")
        if not room:
            return

        unregister_connection()
        leave_room(room)

        if room_service.room_exists(room):
            room_service.remove_member(room)
            emit_presence_update(room_service, room)

        logger.info("%s has left the room %s", name or "unknown user", room)
