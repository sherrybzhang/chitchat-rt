import os

from app import socketio
from app.storage.memory_store import RoomMemoryStore
from app import create_app


def test_presence_updates_on_connect_and_disconnect() -> None:
    os.environ["SECRET_KEY"] = "test-secret"

    room_store = RoomMemoryStore()
    room_store.create("lobby")
    app = create_app(room_store=room_store)
    app.config["TESTING"] = True

    alice_http_client = app.test_client()
    with alice_http_client.session_transaction() as session:
        session["name"] = "alice"
        session["room"] = "lobby"

    alice_socket_client = socketio.test_client(app, flask_test_client=alice_http_client)
    alice_events = alice_socket_client.get_received()
    assert [event for event in alice_events if event["name"] == "message"] == []
    assert {"count": 1} in [event["args"][0] for event in alice_events if event["name"] == "presence"]

    bob_http_client = app.test_client()
    with bob_http_client.session_transaction() as session:
        session["name"] = "bob"
        session["room"] = "lobby"

    bob_socket_client = socketio.test_client(app, flask_test_client=bob_http_client)
    bob_socket_client.get_received()

    alice_events = alice_socket_client.get_received()
    assert [event for event in alice_events if event["name"] == "message"] == []
    assert {"count": 2} in [event["args"][0] for event in alice_events if event["name"] == "presence"]

    bob_socket_client.disconnect()

    alice_events = alice_socket_client.get_received()
    assert [event for event in alice_events if event["name"] == "message"] == []
    assert {"count": 1} in [event["args"][0] for event in alice_events if event["name"] == "presence"]

    alice_socket_client.disconnect()


def test_join_message_emits_only_after_explicit_announce() -> None:
    os.environ["SECRET_KEY"] = "test-secret"

    room_store = RoomMemoryStore()
    room_store.create("lobby")
    app = create_app(room_store=room_store)
    app.config["TESTING"] = True

    alice_http_client = app.test_client()
    with alice_http_client.session_transaction() as session:
        session["name"] = "alice"
        session["room"] = "lobby"

    alice_socket_client = socketio.test_client(app, flask_test_client=alice_http_client)
    alice_socket_client.get_received()

    alice_socket_client.emit("announce_join")

    alice_events = alice_socket_client.get_received()
    assert {"name": "alice", "message": "has entered the room"} in [
        event["args"] for event in alice_events if event["name"] == "message"
    ]

    alice_socket_client.disconnect()


def test_leave_room_route_emits_leave_message_without_disconnect_message() -> None:
    os.environ["SECRET_KEY"] = "test-secret"

    room_store = RoomMemoryStore()
    room_store.create("lobby")
    app = create_app(room_store=room_store)
    app.config["TESTING"] = True

    alice_http_client = app.test_client()
    with alice_http_client.session_transaction() as session:
        session["name"] = "alice"
        session["room"] = "lobby"
        session["rooms"] = ["lobby"]

    bob_http_client = app.test_client()
    with bob_http_client.session_transaction() as session:
        session["name"] = "bob"
        session["room"] = "lobby"

    bob_socket_client = socketio.test_client(app, flask_test_client=bob_http_client)
    bob_socket_client.get_received()

    alice_http_client.post("/leave-room")

    bob_events = bob_socket_client.get_received()
    assert {"name": "alice", "message": "has left the room"} in [
        event["args"] for event in bob_events if event["name"] == "message"
    ]

    bob_socket_client.disconnect()
