from flask import Blueprint, current_app, jsonify, render_template

from .utils import MLClient
from .forms import WaitListSignupForm


mailerlite_app = Blueprint("mailerlite", __name__)
mailerlite = MLClient()

@mailerlite_app.route("/ml-join-waitlist", methods=["GET", "POST"])
def waitlist_form_view():
    form = WaitListSignupForm()
    if form.validate_on_submit():
        email = form.email.data
        GROUP_ID:int = current_app.config["MAILERLITE_WAITLIST_ID"]
        subscriber_id = mailerlite.add_subscriber(email)
        is_added = mailerlite.assign_subscriber(subscriber_id, group_id=GROUP_ID)
        if is_added:
            return jsonify(
                status="success",
                html=render_template("mailerlite/ml-success.html")
            )
        else:
            return jsonify(
                status="fail",
                html=render_template("mailerlite/ml-join-waitlist.html", form=form)
            )
    return render_template("mailerlite/ml-join-waitlist.html", form=form)

@mailerlite_app.route("/ml-sucess", methods=["GET"])
def ml_success_view():
    return render_template("ml-success.html")