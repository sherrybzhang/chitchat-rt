from flask import session
from flask_socketio import join_room, leave_room, send

from app import socketio
from app.services.room_services import room_exists, add_message, add_member, remove_member


def register_socketio_handlers():
    @socketio.on("message")
    def message(data):
        room = session.get("room")
        if not room_exists(room):
            return

        content = {
            "name": session.get("name"),
            "message": data["data"],
        }
        send(content, to=room)
        add_message(room, content)
        print(f"{session.get('name')} said: {data['data']}")

    @socketio.on("connect")
    def connect(auth):
        room = session.get("room")
        name = session.get("name")
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
        room = session.get("room")
        name = session.get("name")
        leave_room(room)

        if room_exists(room):
            remove_member(room)

        send({"name": name, "message": "has left the room"}, to=room)
        print(f"{name} has left the room {room}")
