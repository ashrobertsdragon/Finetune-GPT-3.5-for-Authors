import os
from flask import session

from supabase import create_client, Client
from .utils import email_admin

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def update_db():
    row = session["user_details"]
    try:
        error, response = supabase.table("user").update(row).eq("id", row["id"]).execute()
        return error, response
    except Exception as e:
        email_admin(f"Error {e}\n for {row}")