from flask import Blueprint, current_app, jsonify, render_template

from .utils import add_subscriber, assign_subscriber
from .forms import WaitListSignupForm

mailerlite_app = Blueprint("mailerlite", __name__)

@mailerlite_app.route("/ml-join-waitlist", methods=["GET", "POST"])
def waitlist_form_view():
    form = WaitListSignupForm
    if form.validate_on_submit():
        email = form.email.data
        GROUP_ID = current_app.config["MAILERLITE_WAITLIST_ID"]
        subscriber_id = add_subscriber(email)
        is_added = assign_subscriber(subscriber_id, GROUP_ID)
        if is_added:
            return jsonify(
                status="success",
                html=render_template("mailerlite/ml-success.html")
            )
        else:
            return jsonify(
                status="fail",
                html=render_template("mailerlite/join-waitlist.html")
            )
    render_template("mailerlite/join-waitlist.html")

@mailerlite_app.route("/ml-sucess", methods=["GET"])
def ml_success_view():
    render_template("ml-success.html")