import secrets
import string
from flask import g, session


def load_user():
  g.user = None
  if "access_token" in session:
      g.user = session.get("user_details")

def random_str():
    """Generate a random 7 character alphanumeric string."""
    return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7))
