from flask import session, redirect

from src.supabase import update_db


def update_credits(user):
    session["user_details"]["credits_available"] -= 1
    session["user_details"]["credits_used"] += 1
    credits_available = session["user_details"]["credits_available"]
    update_db()
    if credits_available == 0:
        return redirect("lorebinder-success-buy-credits.html")
    else:
        return redirect("lorebinder-success.html")