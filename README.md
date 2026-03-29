# ChitChat RT

ChitChat RT is a real-time chat application that lets users enter a display name, join or create channels by code, and exchange messages instantly over WebSockets.

***NOTE**: Originally built from scratch in 2023. In 2026, I used AI-assisted development tools to help refactor, modernize, and improve parts of the codebase, including backend fixes and a more polished UI. The architecture, product decisions, and final implementation choices remained mine.*

***NOTE**: This project now uses SQLite for room and message persistence. Restarting the server keeps existing channels and message history, while live member counts reset because presence is session-based.*

## Features
- Display-name entry flow before joining chat
- Create or join a channel by entering a channel code
- Real-time messaging with Flask-SocketIO
- Active channel list with quick switching from the sidebar
- In-room modal for entering another channel without leaving the chat view
- SQLite-backed persistence for rooms and message history
- Message and session validation for empty names, missing channel codes, and invalid Socket.IO payloads

## Technologies
- **Languages:** Python, JavaScript, HTML, CSS
- **Frameworks/Libraries:** Flask, Flask-SocketIO, python-dotenv
- **Transport:** Socket.IO
- **Storage:** SQLite for persistent rooms/messages, in-memory member counts for live presence

## Setup
1) Create and activate a virtual environment.
```bash
python3 -m venv .venv
source .venv/bin/activate
```
2) Install dependencies.
```bash
pip install -r requirements.txt
```
3) Configure environment variables.
```bash
cp .env.example .env
```
Set `SECRET_KEY` in `.env` before starting the app. `DATABASE_PATH` is optional and defaults to `instance/chitchat.db`.

4) Run the app.
```bash
python3 application.py
```
5) Open the app in your browser.
```text
http://localhost:8080
```

## Usage
1. Enter a display name on the landing page.
2. Enter a channel code to join an existing channel or create a new one.
3. Send messages from the room view and watch updates appear in real time.
4. Use the sidebar or the "Enter another channel" modal to switch into a different channel.

## Routes
`GET /` shows the landing page for entering a display name.

`GET, POST /chatroom-entry` lets a user enter a channel code and join or create a channel.

`GET /room` loads the active channel for the current session.

`GET /room/<room_code>` opens a specific channel URL and stores that channel in the current session.

## Tests
The project includes unit tests for room entry behavior, room validation, Socket.IO session/message validation, and SQLite storage behavior.

```bash
pytest
```
