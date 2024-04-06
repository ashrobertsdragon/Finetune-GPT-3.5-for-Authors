import json
import os
import time
from typing import Optional

import stripe
from flask import flash, current_app

from src.error_handling import email_admin

def set_stripe_key():
    stripe.api_key = current_app.config["STRIPE_KEY"]

def get_id(num_credits: int) -> str:
    """
    Extracts the SKU value from a JSON file based on the num_credits key.

    Parameters:
    - file_path: The path to the JSON file.
    - num_credits: The key to look for in the 'stripeIDs' dictionary.

    Returns:
    - The SKU value associated with the given num_credits key.
    """
    file_path = os.path.join("src", "stripe", "stripe-ids.json")
    with open(file_path, 'r') as file:
        data = json.load(file)

    price_id = data.get('stripeIDs', {}).get(str(num_credits))
    return price_id

def handle_error(error: Exception, override_default: bool = False) -> Optional[str]:
    """
    Handle different types of errors that may occur during the payment process.

    Parameters:
    - error: The error object.
    - override_default: Whether to display the default erorr message or
      user_message string from error object (default: False).

    Returns:
    - None

    """

    email_admin(error)
    if override_default:
        flash(error.user_message, "error")
        
    else:
        flash("There was an issue completing your order. Your card was not charged. Please try again later", "error")
    return

def retry_delay(attempt: int) -> int:
    """
    Introduce a delay of 0.5 seconds and increment the attempt count by 1.

    Parameters:
    - attempt: The current attempt count.

    Returns:
    - The updated attempt count.

    """

    time.sleep(0.5)
    return attempt + 1

def create_stripe_session(num_credits: int, customer_email: str, attempt: int = 0) -> Optional[stripe.checkout.Session]:
    """
    Create a Stripe session for a payment.

    Parameters:
    - num_credits: The number of credits being purchased.
    - customer_email: The email address of the customer.
    - attempt: The number of attempts made to create the session (default: 0).

    Returns:
    - The created Stripe session if successful.
    - A recursive call to the function under certain circumstances.
    - None: If an error occurs.

    Raises:
    - stripe.error.CardError: If there is an error with the customer's card.
    - stripe.error.RateLimitError: If the API rate limit is exceeded.
    - stripe.error.APIConnectionError: If there is an error connecting to the Stripe API.
    - Exception: If any other error occurs.
    """
    DOMAIN = current_app.config["DOMAIN"]
    price_id = get_id(num_credits)
    try:
        stripe_session = stripe.checkout.Session.create(
            ui_mode="embedded",
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            customer_email=customer_email,
            return_url=DOMAIN + "/return.html?session_id={CHECKOUT_SESSION_ID}",
            automatic_tax={"enabled": True},
            metadata={"num_credits": num_credits},
        )
        return stripe_session
    except stripe.CardError as e:
        return handle_error(e, override_default=True)
    except (stripe.RateLimitError, stripe.APIConnectionError) as e:
        attempt = retry_delay(attempt)
        if attempt < 2:
            return create_stripe_session(price_id, customer_email, attempt)
        else:
            return handle_error(e)
    except Exception as e:
        return handle_error(e)
