import os

from app import create_app, socketio
from app.storage.memory_store import RoomMemoryStore


def test_unread_update_emits_for_joined_room_when_viewing_another_room() -> None:
    os.environ["SECRET_KEY"] = "test-secret"

    room_store = RoomMemoryStore()
    room_store.create("abc")
    room_store.create("xyz")
    app = create_app(room_store=room_store)
    app.config["TESTING"] = True

    alice_http_client = app.test_client()
    with alice_http_client.session_transaction() as session:
        session["name"] = "alice"
        session["room"] = "abc"
        session["rooms"] = ["abc"]

    alice_socket_client = socketio.test_client(app, flask_test_client=alice_http_client)
    alice_socket_client.get_received()

    sherry_http_client = app.test_client()
    with sherry_http_client.session_transaction() as session:
        session["name"] = "sherry"
        session["room"] = "xyz"
        session["rooms"] = ["abc", "xyz"]

    sherry_socket_client = socketio.test_client(app, flask_test_client=sherry_http_client)
    sherry_socket_client.get_received()

    alice_socket_client.emit("message", {"data": "hello"})

    sherry_events = sherry_socket_client.get_received()
    assert {"room": "abc", "increment": 1} in [
        event["args"][0] for event in sherry_events if event["name"] == "unread_update"
    ]

    alice_socket_client.disconnect()
    sherry_socket_client.disconnect()
