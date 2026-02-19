import logging

from app import create_app, socketio

logging.basicConfig(level=logging.INFO)

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, port="8080")
