import os
from pathlib import Path

from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv

from app.services.room_services import RoomService
from app.storage.memory_store import RoomMemoryStore
from app.storage.room_store import RoomStore

socketio = SocketIO()


def create_app(room_store: RoomStore | None = None) -> Flask:
    repo_root = Path(__file__).resolve().parent.parent
    load_dotenv(repo_root / ".env")
    app = Flask(
        __name__,
        template_folder=str(repo_root / "templates"),
        static_folder=str(repo_root / "static"),
    )
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY is not set. Add it to your environment or .env before running the app.")
    app.config["SECRET_KEY"] = secret_key
    socketio.init_app(app)
    store = room_store if room_store is not None else RoomMemoryStore()
    room_service = RoomService(store)
    app.extensions["room_service"] = room_service
    from app.http.routes import register_routes
    from app.realtime.events import register_socketio_handlers
    register_routes(app, room_service)
    register_socketio_handlers(room_service)
    return app
