from flask import current_app, flash, g, session

from .forms import AccountManagementForm

from prosepal.file_handling import create_signed_url
from prosepal.utils import load_supabasedb


def initialize_user_db() -> bool:
    """
    Inserts user details into the 'user' table in the database.

    Returns:
        boolean of whether row insert was successful.
    """
    if not g.db:
        load_supabasedb()
    info: dict = session["user_details"]
    return g.db.insert_row(table_name="user", data=info, use_service_role=True)


def get_binders() -> list[dict]:
    """
    Get a list of binders owned by the current user.

    Returns:
        binders_list (list): A list of dictionaries containing binder
            information. Each dictionary contains the following keys:
                title (str): The title of the binder.
                author (str): The author of the binder.
                download_path (str): The download path of the binder.
                created_on (str): The date the binder was created.
    """
    db = load_supabasedb()
    owner: int = session["user_details"]["id"]
    match_dict: dict = {"owner": owner}
    binder_data: list = db.select_row(
        table_name="binders",
        match=match_dict,
        columns=["title", "author", "download_path", "created_on"],
    )
    binders_list: list = replace_empty_path(binder_data)
    session["binders_list"] = binders_list
    return binders_list


def replace_empty_path(binder_data: list) -> list[dict]:
    """
    Replace empty download paths with a placeholder string.

    Args:
        binder_data (list): A list of dictionaries

    Returns:
        binders_db (list): A list of modified dictionaries with a key of
            'signed_url' added.
    """
    for binder in binder_data:
        binder["signed_url"] = get_signed_url_or_placeholder(
            binder.get("download_path", "")
        )
    return binder_data


def get_signed_url_or_placeholder(download_path: str) -> str:
    """
    Get a signed URL for the download path, or return a placeholder if not a
    valid URL.

    Args:
        download_path (str): The combined path, not including bucket, of the
            file to be downloaded.

    Returns:
        signed_url (str): The signed URL of the download file, or a
            placeholder text of 'Please check again later' if no an empty
            string is returned or the download_path was not valid
    """
    bucket: str = "binders"
    signed_url: str = (
        create_signed_url(bucket, download_path)
        if is_link(download_path)
        else ""
    )
    return signed_url or "Please check again later"


def is_link(download_path: str) -> bool:
    "Checks if the download_path variable is a text file"
    return False or download_path.endswith(".txt")


def get_user_data(auth_id: str) -> dict:
    """
    Fetches user data from the database based on the provided authentication
        ID.

    Args:
        auth_id (str): The authentication ID of the user.

    Returns:
        dict: A dictionary containing the user data fetched from the database.
    """
    db = load_supabasedb()
    match_dict: dict = {"auth_id": auth_id}
    data = db.select_row(table_name="user", match=match_dict)
    return data[0]


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

    data: dict = get_user_data(auth_id) if auth_id else {}
    if data:
        session["user_details"] = data
        credits_available: int = session["user_details"].get(
            "credits_available"
        )
        return check_credits(credits_available)
    else:
        flash("Error logging in. Please try again later", "error")
        return "accounts.logout_view"


def preload_account_management_form():
    """
    Preloads the account management form with user details from the session.

    Returns:
        AccountManagementForm: The preloaded account management form.
    """
    account_form = AccountManagementForm()
    account_form.email.data = session["user_details"].get("email", "")
    if session["user_details"]["f_name"]:
        account_form.first_name.data = session["user_details"].get(
            "f_name", ""
        )
    if session["user_details"]["l_name"]:
        account_form.last_name.data = session["user_details"].get("l_name", "")
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
            data = auth.update_user({"email": new_email})
            access_token: str = data.session.access_token
            session["access_token"] = access_token
        except Exception as e:
            current_app.logger.error("Unexpected error: %s", str(e))
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
        if key in session["user_details"]:
            if not value:
                continue
            if session["user_details"][key] == value:
                continue
            else:
                session["user_details"][key] = value
        else:
            e = f"{key} not found in {session["user_details"].keys()}"
            current_app.logger.error("Unexpected error: %s", str(e))
