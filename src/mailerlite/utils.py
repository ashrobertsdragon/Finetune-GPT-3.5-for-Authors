import logging

import mailerlite as MailerLite
from decouple import config

error_logger = logging.getLogger("error_logger")
info_logger = logging.getLogger("info_logger")

class MLClient(object):
    
    def __init__(self):
        try:
            ML_KEY:str = config("MAILERLITE_KEY")
            self.client = MailerLite.Client({
                "api_key": ML_KEY
            })
            info_logger.info("MailerLite client connected")
        except Exception as e:
            error_logger.error(f"MailerLite client failed to connect: {e}")

    def add_subscriber(self, email:str) -> int:
        try:
            response = self.client.subscribers.create(email)
            info_logger.info(f"{email} added to Mailerlite")
        except TypeError as e:
            error_logger.error(f"{e}: {email} could not be added")
        except Exception as e:
            error_logger.error(e)
        return response.json()["subscriber_id"]

    def assign_subscriber(self, subscriber_id:int, group_id:int) -> bool:
        try:
            self.client.subscribers.assign_subscriber_to_group(subscriber_id, group_id)
            return True
        except TypeError as e:
            error_logger.error(
                f"{e}: {subscriber_id} could not be added to group {group_id}"
            )
            return False