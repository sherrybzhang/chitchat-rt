import logging

from flask import session
from flask_socketio import join_room, leave_room, send

from app import socketio
from app.services.room_services import RoomService
from app.services.socketio_validation import validate_message_payload, validate_socket_session

logger = logging.getLogger(__name__)


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
        send({"name": name, "message": "has entered the room"}, to=room)
        room_service.add_member(room)
        logger.info("%s joined room %s", name, room)

    @socketio.on("disconnect")
    def disconnect() -> None:
        room, name = validate_socket_session(session.get("room"), session.get("name"))
        if not room or not name:
            return

        leave_room(room)

        if room_service.room_exists(room):
            room_service.remove_member(room)

        send({"name": name, "message": "has left the room"}, to=room)
        logger.info("%s has left the room %s", name, room)
