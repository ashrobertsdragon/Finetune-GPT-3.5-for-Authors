import secrets
import string
from flask import g, session

from .supabase import SupabaseDB

db = SupabaseDB()


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
    auth_id = session["user_details"].get("auth_id")
    match = {"auth_id": auth_id}
    db.update_row("user", info=session["user_details"], match=match)

