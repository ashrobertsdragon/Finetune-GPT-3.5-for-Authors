from flask import session, redirect, url_for, flash
from markupsafe import Markup
from src.supabase import supa_service, supabase



def initialize_user_db(auth_id, email):
    supa_service.table("user").insert({
        "auth_id": auth_id,
        "email": email,
    }).execute()

def get_binders():
    owner = session["user_details"]["id"]
    data = supabase.table("binders").select("title", "author", "download_path").eq("owner", owner).execute()
    if data:
        binder_db = [{"title": binder["title"], "author": binder["author"], "download_path": binder["download_path"]} for binder in data.data]
    else:
        binder_db = []
    return binder_db

def redirect_after_login(auth_id):
    try:
        response = supabase.table("user").select("*").eq("auth_id", auth_id).execute()
        user_details = response.data[0]
        session["user_details"] = user_details
        credits_available = session["user_details"]["credits_available"]
        if credits_available > 0:
            return redirect(url_for("binders.lorebinder_form_view"))
        else:
            return redirect(url_for("accounts.buy_credits_view"))
    except Exception as e:
        flash(e)