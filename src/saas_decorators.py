from functools import wraps
from flask import redirect, session, url_for


def credit_required(f):
    """
    Decorator function that checks if the user has enough credits available
    to access a certain route.

    Parameters:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.

    Notes:
        This decorator function is intended to be used with Flask routes. It
        checks if the user has enough credits available in their session to
        access a certain route. If the user has enough credits, the original
        function is called. If not, the user is redirected to the "buy_credits"
        route.

    Example:
        @app.route("/protected")
        @credit_required
        def protected_route():
            return "This route requires credits"
"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["user_details"]["credits_available"] > 0:
            return f(*args, **kwargs)
        else:
            return redirect(url_for("buy_credits"))
    return decorated_function

def login_required(f):
    """
    Decorator function that requires a user to be logged in to access a
    certain route.

    Parameters:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function that checks the session for an 
        'access_token'. If the 'access_token' is not present, it redirects the
        user to the login page. Otherwise, it proceeds to call the original
        function.

    Notes:
        This decorator is intended for use with Flask routes to ensure that a
        user is authenticated before accessing certain routes. If the user is
        not authenticated, they are redirected to the login page to encourage
        a login attempt. This is a common pattern in web applications to
        protect routes that require a user to be logged in.
    """
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "access_token" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function