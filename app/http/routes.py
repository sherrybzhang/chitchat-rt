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

    @app.route("/chatroomEntry", methods=["POST", "GET"])
    def chatroomEntry():
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
            return redirect(url_for("chatroomEntry"))

        return render_template("room.html", **room_context)

    @app.route("/room/<roomCode>")
    def view_room(roomCode):
        if not room_exists(roomCode):
            return redirect(url_for("chatroomEntry"))

        session["room"] = roomCode
        session.modified = True

        # Set the cookie
        response = make_response(redirect(url_for("room")))
        response.set_cookie("roomCode", roomCode)
        return response

    @app.route("/newRoom", methods=["POST", "GET"])
    def newRoom():
        if request.method == "POST":
            return render_template("chatroomEntry.html")

        return redirect(url_for("chatroomEntry"))

    @app.route("/viewChannel", methods=["POST", "GET"])
    def viewChannel():
        if request.method == "POST":
            room = request.form["room"]
            print(room)
            session["room"] = room
            room_context, room_access_error = build_room_view_context(
                name=session.get("name"),
                room_code=room,
            )
            if room_access_error:
                return redirect(url_for("chatroomEntry"))

            return render_template("room.html", **room_context)

        return redirect(url_for("chatroomEntry"))

    return app
