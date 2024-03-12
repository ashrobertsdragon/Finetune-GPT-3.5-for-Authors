from flask import session, redirect

from src.supabase_client import supabase
from src.utils import send_mail
def update_user_credits(user, credits_available, credits_used):
    try:
        supabase.table("user").update({"credits_available": credits_available, "credits_used": credits_used}).filter("user", eq=user).execute()
    except Exception as e:
        send_mail(f"Exception {e} updating {user} credits")

def update_credits(user):
    session["user_details"]["credits_available"] -= 1
    session["user_details"]["credits_used"] += 1
    credits_available = session["user_details"]["credits_available"]
    credits_used = session["user_details"]["credits_used"]
    update_user_credits(user, credits_available, credits_used)
    if credits_available == 0:
        return redirect("lorebinder-success-buy-credits.html")
    else:
        return redirect("lorebinder-success.html")