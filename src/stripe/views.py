from decouple import config
from flask import Blueprint, jsonify, request, render_template, session

import stripe

from src.decorators import login_required
from src.utils import update_db

from .utils import create_stripe_session, set_stripe_key


stripe_app = Blueprint("stripe", __name__)

stripe.api_key = None

@stripe_app.route("/create_checkout_session", methods=["GET", "POST"])
@login_required
def create_checkout_session():
    customer_email = session["user_details"]["email"]
    num_credits = request.args.get("num_credits", type=int)
    if not stripe.api_key:
        set_stripe_key()
    stripe_session = create_stripe_session(num_credits, customer_email)
    if stripe_session:
        return jsonify(clientSecret=stripe_session.client_secret)

@stripe_app.route("/session-status", methods=["GET"])
@login_required
def session_status():
    stripe_session = stripe.checkout.Session.retrieve(request.args.get("session_id"))
    num_credits = stripe_session.metadata.num_credits
    if stripe_session.status == "paid":
        session["user_details"]["credits_available"] += num_credits
        update_db()

    return jsonify(
        status=stripe_session.status,
        customer_email=stripe_session.customer_details.email
    )

@stripe_app.route('/get_publishable_key', methods=['GET'])
def get_publishable_key():
    STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLIC_KEY")
    return jsonify({'publishable_key': STRIPE_PUBLISHABLE_KEY})

@stripe_app.route("/checkout", methods=['GET'])
def checkout_view():
    num_credits = request.args.get("num_credits")
    return render_template("stripe/checkout.html", num_credits=num_credits)
