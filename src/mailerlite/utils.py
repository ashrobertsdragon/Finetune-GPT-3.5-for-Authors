import logging

import mailerlite as MailerLite
from flask import current_app

error_logger = logging.getLogger("error_logger")
info_logger = logging.getLogger("info_logger")

try:
    MK_KEY = current_app.config["MAILERLITE_KEY"]
    client = MailerLite.Client({
        "api_key": "ML_KEY"
    })
    info_logger("MailerLite client connected")
except Exception as e:
    error_logger(f"MailerLite client failed to connect: {e}")

def add_subscriber(email:str) -> int:
    try:
        response = client.subscribers.create(email)
        info_logger(f"{email} added to Mailerlite")
    except TypeError as e:
        error_logger(f"{e}: {email} could not be added")
    except Exception as e:
        error_logger(e)
    return response.json()["subscriber_id"]

def assign_subscriber(subscriber_id:int, group_id:int) -> bool:
    try:
        client.subscribers.assign_subscriber_to_group(subscriber_id, group_id)
        return True
    except TypeError as e:
        error_logger(
            f"{e}: {subscriber_id} could not be added to group {group_id}"
        )
        return False