"""Minimal user model for session-backed authentication hooks."""
class User:
    def __init__(self, name: str) -> None:
        self.name = name

    def is_authenticated(self) -> bool:
        return True

    def is_active(self) -> bool:
        return True

    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> str:
        return self.name
