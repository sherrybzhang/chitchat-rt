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
    assert {"name": "alice", "message": "has entered the room"} in [
        event["args"] for event in alice_events if event["name"] == "message"
    ]
    assert {"count": 1} in [event["args"][0] for event in alice_events if event["name"] == "presence"]

    bob_http_client = app.test_client()
    with bob_http_client.session_transaction() as session:
        session["name"] = "bob"
        session["room"] = "lobby"

    bob_socket_client = socketio.test_client(app, flask_test_client=bob_http_client)
    bob_socket_client.get_received()

    alice_events = alice_socket_client.get_received()
    assert {"name": "bob", "message": "has entered the room"} in [
        event["args"] for event in alice_events if event["name"] == "message"
    ]
    assert {"count": 2} in [event["args"][0] for event in alice_events if event["name"] == "presence"]

    bob_socket_client.disconnect()

    alice_events = alice_socket_client.get_received()
    assert {"name": "bob", "message": "has left the room"} in [
        event["args"] for event in alice_events if event["name"] == "message"
    ]
    assert {"count": 1} in [event["args"][0] for event in alice_events if event["name"] == "presence"]

    alice_socket_client.disconnect()
