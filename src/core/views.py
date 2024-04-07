from flask import Blueprint, flash, render_template

from .forms import ContactForm
from .utils import send_message, get_update_message

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

    if form.validate_on_submit():
        name = form.name.data
        user_email = form.email.data
        message = form.message.data
        send_message(name, user_email, message)
        flash("Message sent", "success")

    return render_template("core/contact-us.html", form=form)

@core_app.route("/check-update", methods=["GET"])
def check_update_view():
    update_message = get_update_message()
    return render_template("core/updates.html", update_message=update_message)