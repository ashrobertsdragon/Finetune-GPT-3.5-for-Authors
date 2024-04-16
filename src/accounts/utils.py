from flask import session, flash
import logging

from src.supabase import SupabaseDB

from .forms import AccountManagementForm

error_logger = logging.getLogger("error_logger")
db = SupabaseDB()

def initialize_user_db(auth_id: str, email: str) -> None:
    """
    Inserts user details into the 'user' table in the database.

    Args:
        auth_id (str): The authentication ID of the user.
        email (str): The email address of the user.

    """
    info = session["user_details"]
    return db.insert_row(table_name="user", info=info, match={
        "auth_id": auth_id,
        "email": email
    })

def get_binders() -> list:
    """
    Get a list of binders owned by the current user.

    Returns:
        list: A list of dictionaries containing binder information. Each 
            dictionary contains the following keys:
                title (str): The title of the binder.
                author (str): The author of the binder.
                download_path (str): The download path of the binder.
    """
    owner = session["user_details"]["id"]
    match_dict = {"owner": owner}
    binder_data = db.select_row(
        table_name="binders",
        match=match_dict,
        columns=["title", "author", "download_path"]
        )
    if binder_data:
        binder_db = [{
            "title": binder["title"],
            "author": binder["author"],
            "download_path": binder["download_path"]
        } for binder in binder_data.data]
    else:
        binder_db = []
    return binder_db

def get_user_data(auth_id: str) -> dict:
    """
    Fetches user data from the database based on the provided authentication
        ID.

    Args:
        auth_id (str): The authentication ID of the user.

    Returns:
        dict: A dictionary containing the user data fetched from the database.
    """
    match_dict = {"auth_id": auth_id}
    data = db.select_row(table_name="user", match=match_dict)
    return data

def check_credits(credits_available: int) -> str:
    """
    Check the number of credits available and return the corresponding view.

    Args:
        credits_available (int): The number of credits available for the user.

    Returns:
        str: The view to redirect the user based on the value of
        credits_available.
    """
    if credits_available > 0:
        return "binders.lorebinder_form_view"
    else:
        return "accounts.buy_credits_view"

def redirect_after_login(auth_id: str) -> str:
    """
    Redirects the user to a specific view after successful login.

    Args:
        auth_id (str): The authentication ID of the user.

    Returns:
        redirect_str: (str): The name of the view the user should be
            redirected to.
    """
    data = get_user_data(auth_id)
    
    if data:
        session["user_details"] = data[0]
        credits_available = session["user_details"].get("credits_available")
        redirect_str = check_credits(credits_available)
    else:
        flash("Error logging in. Please try again later", "error")
        redirect_str = "accounts.logout_view"

    return redirect_str

def preload_account_management_form():
    """
    Preloads the account management form with user details from the session.

    Returns:
        AccountManagementForm: The preloaded account management form.
    """
    account_form = AccountManagementForm()
    account_form.email.data = session["user_details"].get("email", "")
    if session["user_details"]["f_name"]:
        account_form.first_name.data = session["user_details"].get("f_name","")
    if session["user_details"]["l_name"]:
        account_form.last_name.data = session["user_details"].get("l_name","")
    if session["user_details"]["b_day"]:
        account_form.b_day.data = session["user_details"].get("b_day", "")
    return account_form

def update_email(new_email: str, auth) -> None:
    """
    Update the email address of the user.

    Args:
        new_email (str): The new email address to update.
        auth: The authentication object.

    Returns:
        None

    Raises:
        Exception: If the email update fails.
    """
    if new_email != session["user_details"]["email"]:
        session["user_details"]["email"] = new_email
        try:
            data = auth.update_user(
                {"email": new_email}
            )
            access_token = data.session.access_token
            session["access_token"] = access_token
        except Exception:
            flash("Email update failed", "Error")

def update_user_details(data: dict):
    """
    Update the user details in the session based on the provided data
    dictionary. Iterate over the key-value pairs in the data dictionary and
    check if the value is not empty. If the key exists in the session's 
    "user_details" dictionary and the value is different from the current 
    value, update the value in the session.

    Args:
        data (dict): A dictionary containing the updated user details.

    Returns:
        None
    """
    for key, value in data.items():
        if not value:
            continue
        if key in session["user_details"] \
        and session["user_details"][key] != value:
            session["user_details"][key] = value
