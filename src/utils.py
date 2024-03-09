import secrets
import string

from functools import wraps
from flask import redirect, session


def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if "access_token" not in session:
      return redirect("/login")
    return f(*args, **kwargs)
  return decorated_function

def random_str():
    """Generate a random 7 character alphanumeric string."""
    return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7))