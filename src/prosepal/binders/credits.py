from flask import session

from prosepal.utils import update_db


def update_credits() -> int:
    session["user_details"]["credits_available"] -= 1
    session["user_details"]["credits_used"] += 1
    update_db()
    return session["user_details"]["id"]
