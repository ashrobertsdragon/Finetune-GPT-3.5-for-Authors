import  json
import os
from flask import jsonify, request

import stripe

from src import app
# This is your test secret API key.
stripe.api_key = os.environ["STRIPE_TEST_KEY"]
YOUR_DOMAIN = "http://localhost:4242"

with open("stripe-ids.json", "r") as f:
    stripe_ids = json.load(f)["stripeIDs"]

line_items = []
for item_num, sku_num in stripe_ids.items():
    line_items.append({"price": sku_num, "quantity": 1})

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            ui_mode = "embedded",
            line_items = line_items,
            mode="payment",
            return_url=YOUR_DOMAIN + "/return.html?session_id={CHECKOUT_SESSION_ID}",
            automatic_tax={"enabled": True},
        )
    except Exception as e:
        return str(e)

    return jsonify(clientSecret=session.client_secret)

@app.route("/session-status", methods=["GET"])
def session_status():
  session = stripe.checkout.Session.retrieve(request.args.get("session_id"))

  return jsonify(status=session.status, customer_email=session.customer_details.email)
