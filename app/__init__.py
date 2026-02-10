from pathlib import Path

from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO

socketio = SocketIO()
login_manager = LoginManager()


def create_app():
    repo_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(repo_root / "templates"),
        static_folder=str(repo_root / "static"),
    )
    app.config["SECRET_KEY"] = "hjhjsdahhds"
    socketio.init_app(app)
    login_manager.init_app(app)
    return app
