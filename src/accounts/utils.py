from flask import session, redirect, url_for, flash
import logging

from src.supabase import SupabaseDB

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
    db.insert_row(table_name="user", info=info, match={
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

def fetch_user_data(auth_id: str) -> dict:
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

def redirect_after_login(auth_id):
    """
    Redirects the user to a specific view after successful login.

    Args:
        auth_id (str): The authentication ID of the user.

    Returns:
        redirect: A redirect response to the specified view.
    """
    data = fetch_user_data(auth_id)
    
    if data:
        session["user_details"] = data[0]
        credits_available = session["user_details"].get("credits_available")
        redirect_str = check_credits(credits_available)
    else:
        flash("Error logging in. Please try again later", "error")
        redirect_str = "accounts.logout_view"

    return redirect(url_for(redirect_str))
