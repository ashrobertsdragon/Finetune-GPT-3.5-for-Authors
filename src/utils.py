import secrets
import string

from functools import wraps
from flask import redirect, session, url_for

from .supabase import supabase

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

def random_str():
    """Generate a random 7 character alphanumeric string."""
    return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7))

def email_admin():
    pass

def upload_supabase_bucket(user_folder, file, *, bucket):
    """
    Uploads a file to a Supabase storage bucket.

    Args:
        user_folder (str): The user's uuid which acts as their folder name in the 
        storage bucket where the file will be uploaded.
        file (FileStorage): The file to be uploaded, as a Flask FileStorage
        object.
        bucket (str): The name of the bucket to upload the file to. Must be
        specified as a keyword argument

    Returns:
        upload_path (str): The path the file in the storage bucket.

    Raises:
        Exception: If an error occurs during the file upload.

    Notes:
        - The file will be uploaded with the same name as the original file.
        - The file content type will be determined automatically based on the
        file's MIME type.
        - If the file upload is successful, a success flash message will be
        displayed.
        - If the file upload fails, an error flash message will be displayed.
        - Any exceptions that occur during the file upload will be logged and
        an error flash message will be displayed.
    """

    file_name = file.filename
    upload_path = f"{user_folder}/{file_name}"

    try:
        file_content = file.read()
        file_mime_type = file.content_type
        file.seek(0)

        supabase.storage.from_(bucket).upload(
            path=upload_path,
            file=file_content,
            file_options={"content-type": file_mime_type}
        )
    except Exception as e:
        email_admin(e)
    
    return upload_path