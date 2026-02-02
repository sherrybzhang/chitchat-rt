# ChitChat RT

ChitChat RT is a lightweight online messaging service built with Flask and Socket.IO. It provides simple room-based chat with live updates over WebSockets and a minimal UI.

## Features
- Create or join chat rooms by code
- Real-time messaging with Socket.IO
- In-memory room/member/message tracking
- Simple web UI with message history for the active room

## Technologies
- **Languages**: Python, JavaScript, HTML, CSS
- **Frameworks/Libraries**: Flask, Flask-SocketIO, Socket.IO (client)
- **Templating**: Jinja

## Setup
1) Create and activate a virtual environment
2) Install dependencies
3) Run the server

Example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python application.py
```

Then open `http://localhost:8080` in your browser.

## Notes and Limitations (Current)
- Rooms and messages are stored in memory; restarting the server clears all state.
- No persistence, authentication, or rate limiting yet.
- Room codes are user-provided and not auto-generated.

## Roadmap (Planned)
- Update architecture and dependency set
- Add persistence and proper room management
- Improve validation, security, and error handling
- Refresh UI and documentation
