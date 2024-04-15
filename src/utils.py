import logging
import secrets
import string
from flask import g, session

from .supabase import SupabaseDB

db = SupabaseDB()
error_logger = logging.getLogger("error_logger")
info_logger = logging.getLogger("info_logger")

def load_user():
  g.user = None
  if "access_token" in session:
      g.user = session.get("user_details")

def inject_user_context():
    return {'user': g.user}

def random_str():
    """Generate a random 7 character alphanumeric string."""
    return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7))

def update_db() -> None:
    """
    Update the user's row of the user table with the most current session 
    user_details dictionionary
    """
    try:
        auth_id = session["user_details"]["auth_id"]
    except Exception:
        error_logger(f"auth_id not found in {session["user_details"]}")
    try:
        info = session["user_details"]
        if not isinstance(info, dict):
            raise TypeError(f"{info} must be a dictionary. Received type {type(info)}")
    except TypeError as e:
        error_logger(str(e))
    match = {"auth_id": auth_id}
    return db.update_row("user", info=info, match=match)

