from flask import session, redirect, url_for, flash
from src.supabase import SupabaseDB


db = SupabaseDB()

def initialize_user_db(auth_id, email):
    info = session["user_details"]
    db.insert_row("user", info, match = {
        "auth_id": auth_id,
        "email": email
    })

def get_binders():
    owner = session["user_details"]["id"]
    match_dict = {"owner": owner}
    binder_data = db.select_row("binders", match=match_dict, columns=["title", "author", "download_path"])
    if binder_data:
        binder_db = [{"title": binder["title"], "author": binder["author"], "download_path": binder["download_path"]} for binder in binder_data.data]
    else:
        binder_db = []
    return binder_db

def redirect_after_login(auth_id):
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