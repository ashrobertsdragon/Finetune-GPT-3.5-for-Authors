import  json
import os
from flask import jsonify, request, session

import stripe

from src import app
from src.utils import login_required

from .utils import get_id

# This is your test secret API key.
stripe.api_key = os.environ["STRIPE_TEST_KEY"]
YOUR_DOMAIN = "http://localhost:4242"

with open("stripe-ids.json", "r") as f:
    stripe_ids = json.load(f)["stripeIDs"]

line_items = []
for item_num, sku_num in stripe_ids.items():
    line_items.append({"price": sku_num, "quantity": 1})

@app.route("/create-checkout-session", methods=["POST"])
@login_required
def create_checkout_session():
    customer_email = session["user_details"]["email"]
    num_credits = request.args.get("num_Credits")
    price_id = get_id(num_credits)
    try:
        stripe_session = stripe.checkout.Session.create(
            ui_mode = "embedded",
            line_items = {"price": price_id,
                          "quantity": 1},
            mode="payment",
            customer_email=customer_email,
            return_url=YOUR_DOMAIN + "/return.html?session_id={CHECKOUT_SESSION_ID}",
            automatic_tax={"enabled": True},
        )
    except Exception as e:
        return str(e)

    return jsonify(clientSecret=stripe_session.client_secret)

@app.route("/session-status", methods=["GET"])
def session_status():
  stripe_session = stripe.checkout.Session.retrieve(request.args.get("session_id"))

  return jsonify(status=stripe_session.status, customer_email=stripe_session.customer_details.email)
