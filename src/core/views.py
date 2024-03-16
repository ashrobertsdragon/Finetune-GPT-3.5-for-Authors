import os
import requests
from flask import Blueprint, render_template, flash

from src.error_handling import email_admin
from .forms import ContactForm

core_app = Blueprint("core", __name__)

@core_app.route("/")
def landing_page():
    return render_template("core/index.html")

@core_app.route("/privacy")
def privacy_page():
    return render_template("core/privacy.html")

@core_app.route("/terms")
def terms_page():
    return render_template("core/terms.html")

@core_app.route("/contact-us", methods=["GET", "POST"])
def contact_us_view():
    form = ContactForm()
    def check_email(user_email: str) -> bool:
        api_key =    os.environ.get("abstract_api_key")
        url = f"https://emailvalidation.abstractapi.com/v1/?api_key={api_key}&email={user_email}"
        response = requests.get(url).json()
        if response.get("deliverability") != "DELIVERABLE":
            return False
        if not response.get("is_valid_format", {}).get("value"):
            return False
        if not response.get("is_smtp_valid", {}).get("value"):
            return False
        return True
    def send_message(name, user_email, message) -> None:
        if check_email(user_email):
            email_admin(name, user_email, message)
    
    if form.validate_on_submit():
        name = form.name.data
        user_email = form.email.data
        message = form.message.data
        send_message(name, user_email, message)
        flash("Message sent", "success")

    return render_template("core/contact-us.html", form=form)
