from decouple import config
from flask import Blueprint, render_template, redirect

from .utils import add_subscriber
from .forms import WaitListSignupForm


mailerlite_app = Blueprint("mailerlite", __name__)

@mailerlite_app.route("/ml-join-waitlist", methods=["GET", "POST"])
def waitlist_form_view():
    form = WaitListSignupForm()
    if form.validate_on_submit():
        email = form.email.data
        GROUP_ID:int = config("MAILERLITE_WAITLIST_ID")
        response = add_subscriber(email, groups=[GROUP_ID])
        if response.data:
            return redirect(render_template("mailerlite/ml-success.html"))
        elif response.errors:
            error_message = response.errors.get("email", "Invalid email")[0]
            return render_template(
                "mailerlite/ml-join-waitlist.html",
                form=form,
                error_message=error_message
            )
        else:
            return render_template(
                "mailerlite/ml-join-waitlist.html",
                form=form
            )
    return render_template("mailerlite/ml-join-waitlist.html", form=form)

@mailerlite_app.route("/ml-sucess", methods=["GET"])
def ml_success_view():
    return render_template("ml-success.html")