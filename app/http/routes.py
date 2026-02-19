import logging

from flask import Flask, render_template, request, session, redirect, url_for, make_response
from flask.typing import ResponseReturnValue

from app.services.room_services import (
    build_room_view_context,
    room_exists,
    resolve_room_entry,
)
from app.services.room_validation import validate_name

_ROOM_CODE_COOKIE = "room_code"
logger = logging.getLogger(__name__)


def register_routes(app: Flask) -> Flask:
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

            return render_template("chatroom_entry.html")

        return render_template("index.html")

    @app.route("/chatroom-entry", methods=["POST", "GET"])
    def chatroom_entry() -> ResponseReturnValue:
        if request.method == "POST":
            name = session.get("name")
            code = request.form.get("code")
            join = request.form.get("join", False)
            create = request.form.get("create", False)
            room, entry_error = resolve_room_entry(
                name=name,
                code=code,
                wants_join=join != False,
                wants_create=create != False,
            )
            if entry_error:
                return render_template("chatroom_entry.html", error=entry_error, code=code, name=name)

            session["room"] = room
            room_context, room_error = build_room_view_context(name=name, room_code=room)
            if room_error:
                return render_template("chatroom_entry.html", error=room_error, code=code, name=name)

            return render_template("room.html", **room_context)

        return render_template("chatroom_entry.html")

    @app.route("/room")
    def room() -> ResponseReturnValue:
        room_code = request.cookies.get(_ROOM_CODE_COOKIE)
        if room_code and room_exists(room_code):
            session["room"] = room_code
        room = session.get("room")
        room_context, room_access_error = build_room_view_context(
            name=session.get("name"),
            room_code=room,
        )
        if room_access_error:
            return redirect(url_for("chatroom_entry"))

        return render_template("room.html", **room_context)

    @app.route("/room/<room_code>")
    def view_room(room_code: str) -> ResponseReturnValue:
        if not room_exists(room_code):
            return redirect(url_for("chatroom_entry"))

        session["room"] = room_code
        session.modified = True

        # Set the cookie
        response = make_response(redirect(url_for("room")))
        response.set_cookie(_ROOM_CODE_COOKIE, room_code)
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
            room_context, room_access_error = build_room_view_context(
                name=session.get("name"),
                room_code=room,
            )
            if room_access_error:
                return redirect(url_for("chatroom_entry"))

            return render_template("room.html", **room_context)

        return redirect(url_for("chatroom_entry"))

    return app
