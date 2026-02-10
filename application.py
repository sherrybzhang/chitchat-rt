from flask import session

from app import create_app, login_manager, socketio

app = create_app()

@login_manager.user_loader
def load_user(name):
    return session.get("name")

if __name__ == "__main__":
    socketio.run(app, debug=True, port="8080")
