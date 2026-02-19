import os
from pathlib import Path

from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv

socketio = SocketIO()


def create_app():
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
    from app.http.routes import register_routes
    from app.realtime.events import register_socketio_handlers
    register_routes(app)
    register_socketio_handlers()
    return app
