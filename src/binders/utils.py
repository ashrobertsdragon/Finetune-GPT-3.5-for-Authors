import requests

from src.supabase import supabase
from src.error_handling import email_admin


def save_binder_data(data, user):
    try:
        data["owner"] = user
        supabase.table("binder").insert(data).execute()
    except Exception as e:
        email_admin(f"Exception {e} saving {data} to binderTable")

def call_api(api_payload):
    response = requests.post('PP_API_ENDPOINT', json=api_payload)
    if response.status_code != 200:
        email_admin(f"{response.message} for {api_payload}")