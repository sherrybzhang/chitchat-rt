from flask import session

from app import login_manager

def register_auth():
    @login_manager.user_loader
    def load_user(name):
        return session.get("name")
