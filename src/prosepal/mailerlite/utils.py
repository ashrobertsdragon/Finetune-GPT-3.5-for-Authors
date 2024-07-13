from typing import Optional

from decouple import config
from loguru import logger
from mailerlite import Client

ML_KEY: str = config("MAILERLITE_KEY")
try:
    client: Client = Client({"api_key": ML_KEY})
    logger.info("MailerLite client connected")
except Exception as e:
    logger.error(f"MailerLite client failed to connect: {e}")


def create_kwargs(
    *, fields: Optional[dict] = None, groups: Optional[list] = None
) -> dict:
    """
    Create keyword arguments for the mailerlite client.

    Args:
        fields (Optional[dict]): A dictionary containing the fields to be
            included as keyword arguments. Defaults to None.
        groups (Optional[list]): A list of integers representing the groups to
        be included as keyword arguments. Defaults to None.

    Returns:
        dict: A dictionary containing the keyword arguments.

    Raises:
        TypeError: If the 'fields' parameter is not of type dict or if the
            'groups' parameter is not a list of integers.
    """
    kwargs: dict = {}
    try:
        if fields is not None:
            if isinstance(fields, dict):
                kwargs["fields"] = fields
            else:
                raise TypeError(f"Invalid type in fields: {fields}")
        if groups is not None:
            if isinstance(groups, list) and [
                isinstance(val, int) for val in groups
            ]:
                kwargs["groups"] = groups
            else:
                raise TypeError(f"Invalid type in groups: {groups}")
    except TypeError as e:
        logger.error(str(e))

    return kwargs


def add_subscriber(
    email: str,
    *,
    fields: Optional[dict] = None,
    groups: Optional[list[int]] = None,
):
    """
    Add a subscriber to MailerLite.

    Args:
        email (str): The email address of the subscriber.
        fields (Optional[dict]): Additional fields for the subscriber
            (default: None).
        groups (Optional[list]): Groups to add the subscriber to
            (default: None).

    Returns:
        dict: The response from the MailerLite API.

    Raises:
        TypeError: If there is an issue with the input arguments.
        Exception: If there is an unexpected error.

    Example:
        add_subscriber(
            "example@example.com",
            fields={"name": "John Doe"},
            groups=["123456", "987654"])
    """
    kwargs: dict = create_kwargs(fields=fields, groups=groups)

    try:
        response = client.subscribers.create(email, **kwargs)
        logger.info(f"{email} added to Mailerlite")
        return response.json()
    except TypeError as e:
        logger.error(f"{e}: {email} could not be added")
    except Exception as e:
        logger.error(e)


def create_fields_dict(**kwargs) -> dict:
    return kwargs
