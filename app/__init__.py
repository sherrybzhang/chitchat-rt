"""Application factory and lazily initialized Socket.IO access."""
from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flask import Flask
    from app.storage.room_store import RoomStore
    from flask_socketio import SocketIO


class _SocketIOProxy:
    """Delay Socket.IO construction until the app factory configures it."""
    def __init__(self) -> None:
        self._socketio: SocketIO | None = None

    def _get_socketio(self) -> SocketIO:
        if self._socketio is None:
            from flask_socketio import SocketIO

            self._socketio = SocketIO()
        return self._socketio

    def __getattr__(self, name: str) -> Any:
        return getattr(self._get_socketio(), name)


socketio = _SocketIOProxy()


def create_app(room_store: RoomStore | None = None) -> Flask:
    """
    Build the Flask app with environment-backed config and room services.

    Args:
        room_store: Optional storage backend override, primarily for tests.

    Returns:
        A configured Flask application instance with HTTP routes and Socket.IO handlers registered.
    """
    from dotenv import load_dotenv
    from flask import Flask

    from app.services.room_services import RoomService
    from app.storage.sqlite_store import SQLiteRoomStore

    repo_root = Path(__file__).resolve().parent.parent
    load_dotenv(repo_root / ".env")
    app = Flask(__name__)
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY is not set. Add it to your environment or .env before running the app.")
    app.config["SECRET_KEY"] = secret_key
    socketio.init_app(app)
    database_path = Path(os.environ.get("DATABASE_PATH", "instance/chitchat.db")).expanduser()
    if not database_path.is_absolute():
        # Keep relative database paths anchored to the repo for predictable local runs
        database_path = repo_root / database_path
    store = room_store if room_store is not None else SQLiteRoomStore(database_path)
    room_service = RoomService(store)
    app.extensions["room_service"] = room_service
    from app.http.routes import register_routes
    from app.realtime.events import register_socketio_handlers
    register_routes(app, room_service)
    register_socketio_handlers(room_service)
    return app
