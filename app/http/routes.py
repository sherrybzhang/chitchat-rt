from flask import render_template, request, session, redirect, url_for, make_response

from app.services.room_services import (
    create_room,
    get_room_messages,
    list_rooms,
    room_exists,
    validate_name,
    validate_room_access,
    validate_create_request,
    validate_join_request,
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

    @app.route("/chatroomEntry", methods=["POST", "GET"])
    def chatroomEntry():
        if request.method == "POST":
            name = session.get("name")
            code = request.form.get("code")
            join = request.form.get("join", False)
            create = request.form.get("create", False)
            room = code

            if join != False:
                join_error = validate_join_request(code)
                if join_error:
                    return render_template("chatroomEntry.html", error=join_error, code=code, name=name)

            if create != False:
                create_error = validate_create_request(code)
                if create_error:
                    return render_template("chatroomEntry.html", error=create_error, code=code, name=name)

            if create != False and not room_exists(room):
                create_room(room)
            elif not room_exists(code):
                return render_template(
                    "chatroomEntry.html",
                    error=validate_join_request(code),
                    code=code,
                    name=name,
                )
            session["room"] = room
            return render_template(
                "room.html",
                rooms=list_rooms(),
                code=code,
                name=name,
                messages=get_room_messages(room),
            )

        return render_template("chatroomEntry.html")

    @app.route("/room")
    def room():
        roomCode = request.cookies.get("roomCode")
        if roomCode and room_exists(roomCode):
            session["room"] = roomCode
        room = session.get("room")
        room_access_error = validate_room_access(room, session.get("name"))
        if room_access_error:
            return redirect(url_for("chatroomEntry"))

        return render_template("room.html", code=room, rooms=list_rooms(), messages=get_room_messages(room))

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

    @app.route("/viewChannel", methods=["POST", "GET"])
    def viewChannel():
        if request.method == "POST":
            room = request.form["room"]
            print(room)
            session["room"] = room
            room_access_error = validate_room_access(room, session.get("name"))
            if room_access_error:
                return redirect(url_for("chatroomEntry"))

            return render_template("room.html", code=room, rooms=list_rooms(), messages=get_room_messages(room))

    return app
