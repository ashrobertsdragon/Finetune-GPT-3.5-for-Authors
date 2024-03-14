import json
import time
from typing import Optional

import stripe

from src.utils import email_admin


def get_id(file_path: str, num_credits: int) -> str:
    """
    Extracts the SKU value from a JSON file based on the num_credits key.

    Parameters:
    - file_path: The path to the JSON file.
    - num_credits: The key to look for in the 'stripeIDs' dictionary.

    Returns:
    - The SKU value associated with the given num_credits key.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    price_id = data.get('stripeIDs', {}).get(num_credits)
    
    return price_id

def handle_error(error: Exception, display_message: bool = False) -> Optional[str]:
    """
    Handle different types of errors that may occur during the payment process.

    Parameters:
    - error: The error object.
    - display_message: Whether to display the error message (default: False).

    Returns:
    - The user message if display_message is True.
    - None otherwise.

    """

    email_admin(error)
    if display_message:
        return error.user_message
    else:
        return None

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

def create_stripe_session(price_id: str, customer_email: str, attempt: int = 0) -> Optional[stripe.checkout.Session]:
    """
    Create a Stripe session for a payment.

    Parameters:
    - price_id: The ID of the price for the product.
    - customer_email: The email address of the customer.
    - attempt: The number of attempts made to create the session (default: 0).

    Returns:
    - The created Stripe session if successful.
    - A recursive call to the function under certain circumstances.
    - The user message if an error occurs during the payment process.
    - None: during other errors.

    Raises:
    - stripe.error.CardError: If there is an error with the customer's card.
    - stripe.error.RateLimitError: If the API rate limit is exceeded.
    - stripe.error.APIConnectionError: If there is an error connecting to the Stripe API.
    - Exception: If any other error occurs.

    """

    try:
        stripe_session = stripe.checkout.Session.create(
            ui_mode="embedded",
            line_items={"price": price_id, "quantity": 1},
            mode="payment",
            customer_email=customer_email,
            return_url="/return.html?session_id={CHECKOUT_SESSION_ID}",
            automatic_tax={"enabled": True},
        )
        return stripe_session
    except stripe.error.CardError as e:
        return handle_error(e, display_message=True)
    except (stripe.error.RateLimitError, stripe.error.APIConnectionError) as e:
        attempt = retry_delay(attempt)
        if attempt < 3:
            return create_stripe_session(price_id, customer_email, attempt)
        else:
            return handle_error(e)
    except Exception as e:
        return handle_error(e)
