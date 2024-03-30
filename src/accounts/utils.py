from flask import session, redirect, url_for, flash
from src.supabase import SupabaseDB


db = SupabaseDB()

def initialize_user_db(auth_id: str, email: str) -> None:
    """
    Inserts user details into the 'user' table in the database.

    Args:
        auth_id (str): The authentication ID of the user.
        email (str): The email address of the user.

    """
    info = session["user_details"]
    db.insert_row("user", info, match = {
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
    binder_data = db.select_row("binders", match=match_dict, columns=["title", "author", "download_path"])
    if binder_data:
        binder_db = [{"title": binder["title"], "author": binder["author"], "download_path": binder["download_path"]} for binder in binder_data.data]
    else:
        binder_db = []
    return binder_db

def redirect_after_login(auth_id):
    """
    Redirects the user after login based on their available credits.

    Args:
        auth_id (str): The authentication ID of the user.

    Returns:
        list: A list of dictionaries containing binder information, including
            title, author, and download path.

    Raises:
        Exception: If there is an error retrieving the user details or 
            selecting binder data from the database.
    """
    try:
        match_dict = {"auth_id": auth_id}
        response = db.select_row("user", match=match_dict)
        user_details = response.data[0]
        session["user_details"] = user_details
        credits_available = session["user_details"]["credits_available"]
        if credits_available > 0:
            return redirect(url_for("binders.lorebinder_form_view"))
        else:
            return redirect(url_for("accounts.buy_credits_view"))
    except Exception as e:
        flash(e)