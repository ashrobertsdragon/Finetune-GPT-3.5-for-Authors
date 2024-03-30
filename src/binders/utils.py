import requests

from src.supabase import SupabaseDB
from src.error_handling import email_admin


db = SupabaseDB

def save_binder_data(api_payload: dict, user: str) -> None:
    """
    Save binder data to the database.

    Parameters:
    - api_payload (dict): The data to be saved to the binder table.
    - user (str): The owner of the data.

    Returns:
    None

    Raises:
    - Exception: If there is an error saving the data to the binder table.
    """
    try:
        data = api_payload
        data["owner"] = user
        db.insert_row("binder", data=data)
    except Exception as e:
        email_admin(f"Exception {e} saving {data} to binderTable")

def call_api(api_payload):
    response = requests.post('PP_API_ENDPOINT', json=api_payload)
    if response.status_code != 200:
        email_admin(f"{response.message} for {api_payload}")