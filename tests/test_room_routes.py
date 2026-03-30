import os

from app import create_app
from app.storage.memory_store import RoomMemoryStore


def test_channel_list_is_scoped_to_current_session() -> None:
    os.environ["SECRET_KEY"] = "test-secret"
    app = create_app(room_store=RoomMemoryStore())
    app.config["TESTING"] = True

    sonya = app.test_client()
    tom = app.test_client()

    sonya.post("/chat", data={"name": "sonya"})
    sonya_response = sonya.post("/chatroom-entry", data={"code": "abc"})
    assert b'href="/room/abc"' in sonya_response.data
    assert b'href="/room/xyz"' not in sonya_response.data

    tom.post("/chat", data={"name": "tom"})
    tom.post("/chatroom-entry", data={"code": "xyz"})

    sonya_room_response = sonya.get("/room")
    tom_room_response = tom.get("/room")

    assert b'href="/room/abc"' in sonya_room_response.data
    assert b'href="/room/xyz"' not in sonya_room_response.data
    assert b'href="/room/xyz"' in tom_room_response.data
    assert b'href="/room/abc"' not in tom_room_response.data


def test_joined_rooms_accumulate_for_one_session() -> None:
    os.environ["SECRET_KEY"] = "test-secret"
    app = create_app(room_store=RoomMemoryStore())
    app.config["TESTING"] = True

    client = app.test_client()
    client.post("/chat", data={"name": "sherry"})
    client.post("/chatroom-entry", data={"code": "abc"})
    client.post("/room-modal-entry", data={"code": "xyz"})

    response = client.get("/room")

    assert b'href="/room/abc"' in response.data
    assert b'href="/room/xyz"' in response.data


def test_joined_rooms_keep_original_order_when_revisiting_channel() -> None:
    os.environ["SECRET_KEY"] = "test-secret"
    app = create_app(room_store=RoomMemoryStore())
    app.config["TESTING"] = True

    client = app.test_client()
    client.post("/chat", data={"name": "sherry"})
    client.post("/chatroom-entry", data={"code": "abc"})
    client.post("/room-modal-entry", data={"code": "xyz"})

    response = client.get("/room/abc", follow_redirects=True)
    page = response.get_data(as_text=True)

    assert page.index('href="/room/abc"') < page.index('href="/room/xyz"')
