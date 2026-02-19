from flask import session
from flask_socketio import join_room, leave_room, send

from app import socketio
from app.services.room_services import room_exists, add_message, add_member, remove_member
from app.services.socketio_validation import validate_message_payload, validate_socket_session


def register_socketio_handlers():
    @socketio.on("message")
    def message(data):
        room, name = validate_socket_session(session.get("room"), session.get("name"))
        if not room or not name:
            return
        if not room_exists(room):
            return

        message_text = validate_message_payload(data)
        if message_text is None:
            return

        content = {
            "name": name,
            "message": message_text,
        }
        send(content, to=room)
        add_message(room, content)
        print(f"{name} said: {message_text}")

    @socketio.on("connect")
    def connect(auth):
        if auth is not None and not isinstance(auth, dict):
            return

        room, name = validate_socket_session(session.get("room"), session.get("name"))
        if not room or not name:
            return
        if not room_exists(room):
            leave_room(room)
            return

        join_room(room)
        send({"name": name, "message": "has entered the room"}, to=room)
        add_member(room)
        print(f"{name} joined room {room}")

    @socketio.on("disconnect")
    def disconnect():
        room, name = validate_socket_session(session.get("room"), session.get("name"))
        if not room or not name:
            return

        leave_room(room)

        if room_exists(room):
            remove_member(room)

        send({"name": name, "message": "has left the room"}, to=room)
        print(f"{name} has left the room {room}")
