import requests

from src.supabase import supabase
from src.utils import send_mail


def save_lorebinder_data(data, user):
    try:
        data["owner"] = user
        supabase.table("binder").insert(data).execute()
    except Exception as e:
        send_mail(f"Exception {e} saving {data} to binderTable")

def call_api(api_payload):
    response = requests.post('PP_API_ENDPOINT', json=api_payload)
    if response.status_code != 200:
        send_mail(f"{response.message} for {api_payload}")