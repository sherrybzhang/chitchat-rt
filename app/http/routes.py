from flask import render_template, request, session, redirect, url_for, make_response

rooms = {}


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

            if not name:
                return render_template("index.html", error="* Please enter a name", name=name)

            return render_template("chatroomEntry.html")

    @app.route("/chatroomEntry", methods=["POST", "GET"])
    def chatroomEntry():
        if request.method == "POST":
            name = session.get("name")
            code = request.form.get("code")
            join = request.form.get("join", False)
            create = request.form.get("create", False)
            room = code

            if join != False and not code:
                return render_template("chatroomEntry.html", error="Please enter a room code.", code=code, name=name)

            if create != False and room in rooms:
                return render_template(
                    "chatroomEntry.html",
                    error="Room already exists. Click 'Join a Channel' to join. ",
                    code=code,
                    name=name,
                )

            if create != False and code not in rooms:
                rooms[room] = {"members": 0, "messages": []}
            elif code not in rooms:
                return render_template("chatroomEntry.html", error="Room does not exist.", code=code, name=name)
            session["room"] = room
            return render_template(
                "room.html",
                rooms=rooms,
                code=code,
                name=name,
                messages=rooms[room]["messages"],
            )

        return render_template("chatroomEntry.html")

    @app.route("/room")
    def room():
        roomCode = request.cookies.get("roomCode")
        if roomCode and roomCode in rooms:
            session["room"] = roomCode
        room = session.get("room")
        if room is None or session.get("name") is None or room not in rooms:
            return redirect(url_for("chatroomEntry"))

        return render_template("room.html", code=room, rooms=rooms, messages=rooms[room]["messages"])

    @app.route("/room/<roomCode>")
    def view_room(roomCode):
        if roomCode not in rooms:
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
            if room is None or session.get("name") is None or room not in rooms:
                return redirect(url_for("chatroomEntry"))

            return render_template("room.html", code=room, rooms=rooms, messages=rooms[room]["messages"])

    return app
