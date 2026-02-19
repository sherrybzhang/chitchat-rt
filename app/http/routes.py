from flask import render_template, request, session, redirect, url_for, make_response

from app.services.room_services import (
    build_room_view_context,
    room_exists,
    resolve_room_entry,
    validate_name,
)


def register_routes(app):
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    @app.route("/", methods=["POST", "GET"])
    def index():
        return render_template("index.html")

    @app.route("/chat", methods=["POST", "GET"])
    def chat():
        if request.method == "POST":
            name = request.form.get("name")
            session["name"] = name

            name_error = validate_name(name)
            if name_error:
                return render_template("index.html", error=name_error, name=name)

            return render_template("chatroomEntry.html")

        return render_template("index.html")

    @app.route("/chatroom-entry", methods=["POST", "GET"])
    def chatroom_entry():
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
                return render_template("chatroomEntry.html", error=entry_error, code=code, name=name)

            session["room"] = room
            room_context, room_error = build_room_view_context(name=name, room_code=room)
            if room_error:
                return render_template("chatroomEntry.html", error=room_error, code=code, name=name)

            return render_template("room.html", **room_context)

        return render_template("chatroomEntry.html")

    @app.route("/room")
    def room():
        roomCode = request.cookies.get("roomCode")
        if roomCode and room_exists(roomCode):
            session["room"] = roomCode
        room = session.get("room")
        room_context, room_access_error = build_room_view_context(
            name=session.get("name"),
            room_code=room,
        )
        if room_access_error:
            return redirect(url_for("chatroom_entry"))

        return render_template("room.html", **room_context)

    @app.route("/room/<room_code>")
    def view_room(room_code):
        if not room_exists(room_code):
            return redirect(url_for("chatroom_entry"))

        session["room"] = room_code
        session.modified = True

        # Set the cookie
        response = make_response(redirect(url_for("room")))
        response.set_cookie("roomCode", room_code)
        return response

    @app.route("/new-room", methods=["POST", "GET"])
    def new_room():
        if request.method == "POST":
            return render_template("chatroomEntry.html")

        return redirect(url_for("chatroom_entry"))

    @app.route("/view-channel", methods=["POST", "GET"])
    def view_channel():
        if request.method == "POST":
            room = request.form["room"]
            print(room)
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
