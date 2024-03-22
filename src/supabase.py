from decouple import config
from flask import session

from supabase import create_client, Client
from .error_handling import email_admin

url: str = config("SUPABASE_URL")
key: str = config("SUPABASE_KEY")
service_role: str = config("SUPABASE_SERVICE_ROLE")
supabase: Client = create_client(url, key)
supa_service: Client = create_client(url, service_role)

def update_db():
    row = session["user_details"]
    try:
        response, _ = supabase.table("user").update(row).eq("id", row["id"]).execute()
        return response
    except Exception as e:
        email_admin(f"Error {e}\n for {row}")