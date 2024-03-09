import os
import requests
from flask import Blueprint, render_template

from src import app
from src.utils import send_mail
from .forms import ContactForm

core_bp = Blueprint("core", __name__)

@app.route("/contact-us", methods=["GET", "POST"])
def send_email():
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
            send_mail(name, user_email, message)
    
    if form.validate_on_submit():
        name = form.name.data
        user_email = form.email.data
        message = form.message.data
        send_message(name, user_email, message)
        return render_template("message_sent.html")

    return render_template("contact-us.html", form=form)