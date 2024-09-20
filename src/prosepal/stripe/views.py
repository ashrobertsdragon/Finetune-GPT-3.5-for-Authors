import stripe
from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    session,
)

from prosepal.decorators import login_required
from prosepal.utils import update_db

from .utils import create_stripe_session, set_stripe_key

stripe_app = Blueprint("stripe", __name__)

stripe.api_key = None


@stripe_app.route("/create-checkout-session", methods=["POST"])
@login_required
def create_checkout_session():
    customer_email = session["user_details"]["email"]

    data = request.get_json()
    num_credits = data.get("num_credits")
    if not isinstance(num_credits, int) or num_credits < 1 or num_credits > 10:
        return jsonify({"error": "Invalid number of credits"}), 400

    if not stripe.api_key:
        set_stripe_key()
    stripe_session = create_stripe_session(num_credits, customer_email)
    if stripe_session:
        return jsonify(clientSecret=stripe_session.client_secret)
    else:
        return jsonify(num_credits)


@stripe_app.route("/session-status", methods=["GET"])
@login_required
def session_status():
    try:
        stripe_session = stripe.checkout.Session.retrieve(
            request.args.get("session_id")
        )
        if stripe_session.status == "complete":
            num_credits = int(stripe_session.metadata.num_credits)
            session["user_details"]["credits_available"] += num_credits
            update_db()

        return jsonify(
            status=stripe_session.status,
            customer_email=stripe_session.customer_details.email,
        )
    except stripe.RateLimitError as e:
        current_app.logger.error("Unexpected error: %s", str(e))
        return jsonify(error="Rate limit exceeded"), 429
    except Exception as e:
        current_app.logger.error("Unexpected error: %s", str(e))
        return jsonify(error=str(e)), 500


@stripe_app.route("/get-publishable-key", methods=["GET"])
def get_publishable_key():
    STRIPE_PUBLISHABLE_KEY = current_app.config["STRIPE_PUBLISHABLE_KEY"]
    return jsonify({"publishable_key": STRIPE_PUBLISHABLE_KEY})


@stripe_app.route("/get-available-credits", methods=["GET"])
@login_required
def get_available_credits():
    return jsonify(
        credits_available=session["user_details"]["credits_available"]
    )


@stripe_app.route("/get-domain", methods=["GET"])
def get_domain():
    DOMAIN = current_app.config["DOMAIN"]
    return jsonify({"domain": DOMAIN})


@stripe_app.route("/checkout", methods=["GET"])
@login_required
def checkout_view():
    num_credits = request.args.get("num_credits")
    return render_template("stripe/checkout.html", num_credits=num_credits)


@stripe_app.route("/return", methods=["GET"])
@login_required
def return_view():
    session_id = request.args.get("session_id")
    return render_template("stripe/return.html", session_id=session_id)