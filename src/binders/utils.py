import requests
from flask import current_app

from src.error_handling import email_admin
from src.supabase import SupabaseDB

from .credits import update_credits

db = SupabaseDB()


def save_binder_data(api_payload: dict, user: str) -> None:
    """
    Save binder data to the database.

    Args:
        api_payload (dict): The data to be saved to the binder table.
        user (str): The owner of the data.

    Returns:
        None

    Raises:
        Exception: If there is an error saving the data to the binder table.
    """
    try:
        data = api_payload
        data["owner"] = user
        db.insert_row(table_name="binders", data=data)
    except Exception as e:
        current_app.logger.exception(f"Exception {e} saving {data} to binderTable")
        email_admin(f"Exception {e} saving {data} to binderTable")

def call_api(api_payload: dict, endpoint: str):
    response = requests.post(endpoint, json=api_payload)
    if response.status_code != 200:
        email_admin(f"{response.message} for {api_payload}")
    return response.status_code == 200

def str_to_dedup_list(string:str, *, delim: str = ",") -> list:
    """
    Strips whitespace and extra delimeters from a string and converts to a set
    for deduplication before converting to a string.

    Args:
        string (str): The string to be converted.
        delim (str)): The delimeter used in the string to be converted. Must be
            be used as a keword argument. Comma is used if parameter is not
            given.
    
    Returns:
        list
    """
    cleaned_str = string.strip()
    return list(set(cleaned_str.split(delim)))

def start_binder(api_payload: dict, *, endpoint_name: str) -> bool:
        """
        Save the data for access to the API and call API. Updates credit
        balance and databases and returns boolean of if process has started.

        Args:
            api_payload (dict): Payload to send to API of data assembled from
                web form.
            endpoint_name (str): Lookup name for endpoint in dictionary in
                config file.
        
        Returns:
            bool.
        """
        endpoint=current_app.config["PROSEPAL_ENDPOINTS"][endpoint_name]
        user = update_credits()
        save_binder_data(api_payload, user)
        #return call_api(api_payload, endpoint)
        return True
