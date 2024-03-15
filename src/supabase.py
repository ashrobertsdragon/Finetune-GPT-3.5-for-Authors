from decouple import config
from flask import session

from supabase import create_client, Client
from .error_handling import email_admin

url: str = config("SUPABASE_URL")
key: str = config("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def update_db():
    row = session["user_details"]
    try:
        error, response = supabase.table("user").update(row).eq("id", row["id"]).execute()
        return error, response
    except Exception as e:
        email_admin(f"Error {e}\n for {row}")