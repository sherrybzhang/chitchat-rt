import logging

from flask import Flask, jsonify, make_response, redirect, render_template, request, session, url_for
from flask.typing import ResponseReturnValue

from app import socketio
from app.services.room_services import RoomService
from app.services.room_validation import validate_name

_ROOM_CODE_COOKIE = "room_code"
_SESSION_ROOMS_KEY = "rooms"
_SESSION_PENDING_JOIN_ANNOUNCEMENT_KEY = "pending_room_join_announcement"
logger = logging.getLogger(__name__)


def register_routes(app: Flask, room_service: RoomService) -> Flask:
    def get_session_rooms() -> list[str]:
        raw_rooms = session.get(_SESSION_ROOMS_KEY, [])
        if not isinstance(raw_rooms, list):
            return []

        clean_rooms: list[str] = []
        for room in raw_rooms:
            if not isinstance(room, str):
                continue
            if not room_service.room_exists(room):
                continue
            clean_rooms.append(room)

        return clean_rooms

    def store_session_rooms(rooms: list[str]) -> None:
        session[_SESSION_ROOMS_KEY] = rooms
        session.modified = True

    def remember_room(room_code: str) -> list[str]:
        rooms = get_session_rooms()
        if room_code in rooms:
            return rooms

        rooms.append(room_code)
        store_session_rooms(rooms)
        return rooms

    def forget_room(room_code: str) -> list[str]:
        rooms = [room for room in get_session_rooms() if room != room_code]
        store_session_rooms(rooms)
        return rooms

    def set_pending_join_announcement(room_code: str | None) -> None:
        if room_code:
            session[_SESSION_PENDING_JOIN_ANNOUNCEMENT_KEY] = room_code
        else:
            session.pop(_SESSION_PENDING_JOIN_ANNOUNCEMENT_KEY, None)

    def consume_pending_join_announcement(room_code: str | None) -> bool:
        pending_room = session.pop(_SESSION_PENDING_JOIN_ANNOUNCEMENT_KEY, None)
        return isinstance(pending_room, str) and pending_room == room_code

    def render_room_modal_error(
        *,
        error_message: str,
        name: str | None,
        code: str | None,
        current_room: str | None,
        is_async_request: bool = False,
        chatroom_entry_status_code: int | None = None,
    ) -> ResponseReturnValue:
        if is_async_request:
            return jsonify({"ok": False, "error": error_message}), 400

        room_context, room_context_error = room_service.build_room_view_context(
            name=name,
            room_code=current_room,
            rooms=get_session_rooms(),
        )
        if room_context_error:
            response = render_template("chatroom_entry.html", error=error_message, code=code, name=name)
            if chatroom_entry_status_code is not None:
                return response, chatroom_entry_status_code
            return response

        return (
            render_template(
                "room.html",
                **room_context,
                announce_room_join=False,
                modal_open=True,
                modal_error=error_message,
                modal_code=code,
            ),
            400,
        )

    @app.before_request
    def make_session_permanent() -> None:
        session.permanent = True

    @app.route("/", methods=["POST", "GET"])
    def index() -> ResponseReturnValue:
        return render_template("index.html")

    @app.route("/chat", methods=["POST", "GET"])
    def chat() -> ResponseReturnValue:
        if request.method == "POST":
            name = request.form.get("name")
            session["name"] = name

            name_error = validate_name(name)
            if name_error:
                return render_template("index.html", error=name_error, name=name)

            session.pop("room", None)
            store_session_rooms([])
            set_pending_join_announcement(None)
            return render_template("chatroom_entry.html")

        return render_template("index.html")

    @app.route("/chatroom-entry", methods=["POST", "GET"])
    def chatroom_entry() -> ResponseReturnValue:
        if request.method == "POST":
            name = session.get("name")
            code = request.form.get("code")
            origin = request.form.get("origin")
            is_room_modal_request = origin == "room-modal"

            room, entry_error = room_service.resolve_room_entry(
                name=name,
                code=code,
            )
            if entry_error:
                if is_room_modal_request:
                    return render_room_modal_error(
                        error_message=entry_error,
                        name=name,
                        code=code,
                        current_room=session.get("room"),
                    )
                return render_template("chatroom_entry.html", error=entry_error, code=code, name=name)

            session["room"] = room
            joined_rooms = remember_room(room)
            set_pending_join_announcement(None)
            room_context, room_error = room_service.build_room_view_context(
                name=name,
                room_code=room,
                rooms=joined_rooms,
            )
            if room_error:
                if is_room_modal_request:
                    return render_room_modal_error(
                        error_message=room_error,
                        name=name,
                        code=code,
                        current_room=session.get("room"),
                    )
                return render_template("chatroom_entry.html", error=room_error, code=code, name=name)

            return render_template("room.html", **room_context, announce_room_join=True)

        return render_template("chatroom_entry.html")

    @app.route("/room")
    def room() -> ResponseReturnValue:
        room_code = request.cookies.get(_ROOM_CODE_COOKIE)
        if room_code and room_service.room_exists(room_code):
            session["room"] = room_code
            remember_room(room_code)
        room = session.get("room")
        room_context, room_access_error = room_service.build_room_view_context(
            name=session.get("name"),
            room_code=room,
            rooms=get_session_rooms(),
        )
        if room_access_error:
            return redirect(url_for("chatroom_entry"))

        return render_template("room.html", **room_context, announce_room_join=consume_pending_join_announcement(room))

    @app.route("/room/<room_code>")
    def view_room(room_code: str) -> ResponseReturnValue:
        if not room_service.room_exists(room_code):
            return redirect(url_for("chatroom_entry"))

        session["room"] = room_code
        remember_room(room_code)
        set_pending_join_announcement(None)

        # Set the cookie
        response = make_response(redirect(url_for("room")))
        response.set_cookie(_ROOM_CODE_COOKIE, room_code)
        return response

    @app.route("/leave-room", methods=["POST"])
    def leave_room() -> ResponseReturnValue:
        current_room = session.get("room")
        name = session.get("name")
        if not isinstance(current_room, str) or not current_room:
            return redirect(url_for("chatroom_entry"))
        set_pending_join_announcement(None)

        if isinstance(name, str) and name and room_service.room_exists(current_room):
            socketio.emit("message", {"name": name, "message": "has left the room"}, to=current_room)

        remaining_rooms = forget_room(current_room)
        next_room = remaining_rooms[-1] if remaining_rooms else None

        if next_room:
            session["room"] = next_room
            response = make_response(redirect(url_for("room")))
            response.set_cookie(_ROOM_CODE_COOKIE, next_room)
            return response

        session.pop("room", None)
        response = make_response(redirect(url_for("chatroom_entry")))
        response.delete_cookie(_ROOM_CODE_COOKIE)
        return response

    @app.route("/room-modal-entry", methods=["POST"])
    def room_modal_entry() -> ResponseReturnValue:
        name = session.get("name")
        code = request.form.get("code")
        is_async_request = request.headers.get("X-Requested-With") == "XMLHttpRequest"
        requested_room = (code or "").strip()
        current_room = session.get("room")

        if requested_room and current_room and requested_room == current_room:
            return render_room_modal_error(
                error_message="You are already in this channel",
                name=name,
                code=code,
                current_room=current_room,
                is_async_request=is_async_request,
                chatroom_entry_status_code=400,
            )

        room, entry_error = room_service.resolve_room_entry(
            name=name,
            code=code,
        )
        if entry_error:
            return render_room_modal_error(
                error_message=entry_error,
                name=name,
                code=code,
                current_room=current_room,
                is_async_request=is_async_request,
                chatroom_entry_status_code=400,
            )

        session["room"] = room
        joined_rooms = remember_room(room)
        set_pending_join_announcement(room)
        room_context, room_error = room_service.build_room_view_context(
            name=name,
            room_code=room,
            rooms=joined_rooms,
        )
        if room_error:
            return render_room_modal_error(
                error_message=room_error,
                name=name,
                code=code,
                current_room=session.get("room"),
                is_async_request=is_async_request,
                chatroom_entry_status_code=400,
            )

        if is_async_request:
            response = make_response(jsonify({"ok": True, "room": room, "redirect_url": url_for("room")}))
            response.set_cookie(_ROOM_CODE_COOKIE, room)
            return response

        response = make_response(redirect(url_for("room")))
        response.set_cookie(_ROOM_CODE_COOKIE, room)
        return response

    @app.route("/new-room", methods=["POST", "GET"])
    def new_room() -> ResponseReturnValue:
        if request.method == "POST":
            return render_template("chatroom_entry.html")

        return redirect(url_for("chatroom_entry"))

    @app.route("/view-channel", methods=["POST", "GET"])
    def view_channel() -> ResponseReturnValue:
        if request.method == "POST":
            room = request.form["room"]
            logger.debug("Selected room from channel list: %s", room)
            session["room"] = room
            joined_rooms = remember_room(room)
            room_context, room_access_error = room_service.build_room_view_context(
                name=session.get("name"),
                room_code=room,
                rooms=joined_rooms,
            )
            if room_access_error:
                return redirect(url_for("chatroom_entry"))

            return render_template("room.html", **room_context)

        return redirect(url_for("chatroom_entry"))

    return app
