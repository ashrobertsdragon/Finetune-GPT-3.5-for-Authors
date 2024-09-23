import secrets
import string

from flask import app, g, session
from loguru import logger

from .logging_config import supabase_logger
from .supabase import SupabaseDB
from .supabase_validator import validate

db = None


def load_user():
    g.user = None
    if "access_token" in session:
        g.user = session.get("user_details")


def inject_user_context():
    return {"user": g.user}


def random_str():
    """Generate a random 7 character alphanumeric string."""
    return "".join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(7)
    )


def get_supabasedb() -> SupabaseDB:
    global db
    if db is None:
        client = app.config["SUPABASE_CLIENT"]
        db = SupabaseDB(client, supabase_logger, validate)
    return db


def update_db() -> bool:
    """
    Update the user's row of the user table with the most current session
    user_details dictionary. Returns a boolean of whether update was
    successful.
    """
    db = get_supabasedb()
    try:
        auth_id: str = session["user_details"]["auth_id"]
    except LookupError:
        logger.error(f"auth_id not found in {session["user_details"]}")
    try:
        info: dict = session["user_details"]
        if not isinstance(info, dict):
            raise TypeError(
                f"{info} must be a dictionary. Received type {type(info)}"
            )
    except TypeError as e:
        logger.error(str(e))
    match: dict[str, str] = {"auth_id": auth_id}
    return db.update_row(table_name="user", info=info, match=match)
