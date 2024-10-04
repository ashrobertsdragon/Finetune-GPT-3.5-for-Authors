from datetime import date, timedelta

import requests
from decouple import config
from flask import g

from prosepal.cache import cache
from prosepal.error_handling import email_admin
from prosepal.utils import load_supabasedb


def get_future_date(days_ahead: int) -> date:
    """
    Calculate a future date based on the current date and the number
    of days ahead.

    Parameters:
    - days_ahead (int): The number of days ahead to calculate the future date.

    Returns:
    - date: The calculated future date.

    Example:
    get_future_date(7)
    datetime.date(2022, 1, 8)
    """
    current_date: date = date.today()
    return current_date + timedelta(days=days_ahead)


def get_update_data(check_dates: list[str]) -> list[dict]:
    """
    Get update data for the given check dates.

    Args:
        check_dates (list[str]): A list of dates to check for updates.

    Returns:
        list[dict]: A list of dictionaries containing update information. Each
            dictionary contains the following keys:
                "message" (str): The update message.
                "start_time" (str): The start time of the update.
                "end_time" (str): The end time of the update.

    Example:
        get_update_data(
            ["2022-01-01", "2022-01-02", "2022-01-03", "2022-01-04"]
        )
    [
        {
            "message": "Update 1",
            "start_time": "2022-01-01 10:00:00",
            "end_time": "2022-01-01 12:00:00"
        },
        {
            "message": "Update 2",
            "start_time": "2022-01-02 14:00:00",
            "end_time": "2022-01-02 16:00:00"
        }
    ]
    """
    if not g.db:
        load_supabasedb()
    matches: dict = {"date": check_dates}
    response: list = g.db.select_rows(
        table_name="updates",
        matches=matches,
        columns=["message", "start_time", "end_time"],
    )
    return response.data or [{}]


@cache.cached(timeout=43200, key_prefix="update_messages")
def get_update_message(days_ahead: int) -> list[dict]:
    """
    Get update data for the given check dates.

    Args:
        check_dates (list[str]): A list of dates to check for updates.

    Returns:
        list[dict]: A list of dictionaries containing update information. Each
            dictionary contains the following keys:
                "message" (str): The update message.
                "start_time" (str): The start time of the update.
                "end_time" (str): The end time of the update.

    Example:
        get_update_message(days_ahead=3)
        [
            {
                "message": "Update 1",
                "start_time": "2022-01-01 10:00:00",
                "end_time": "2022-01-01 12:00:00"
            },
            {
                "message": "Update 2",
                "start_time": "2022-01-02 14:00:00",
                "end_time": "2022-01-02 16:00:00"
            }
        ]
    """
    days_ahead: int = config("check_updates_ahead_days")
    check_dates: list = [
        get_future_date(day).isoformat() for day in range(days_ahead + 1)
    ]
    return get_update_data(check_dates) or [{}]


def check_email(email: str) -> bool:
    key: str = config("ABSTRACT_API_KEY")
    api_domain: str = config("ABSTRACT_API_DOMAIN")
    url: str = f"{api_domain}/v1/?api_key={key}&email={email}"

    response: dict = requests.get(url, timeout=10).json()

    if response.get("deliverability") != "DELIVERABLE":
        return False
    if not response.get("is_valid_format", {}).get("value"):
        return False
    return bool(response.get("is_smtp_valid", {}).get("value"))


def send_message(name: str, user_email: str, message: str) -> None:
    if check_email(user_email):
        email_admin(name, user_email, message)
