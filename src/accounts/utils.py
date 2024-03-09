from src.utils import random_str
from src.supabase_client import supabase


def create_user(user_id):
    while True:
        user_prefix = random_str()
        res = supabase.table("userTable").insert({
            "user_id": user_id,
            "user_prefix": user_prefix,
        }).execute()
        if not res.error:
            break
        elif "unique constraint" in res.error.message.lower():
            continue
