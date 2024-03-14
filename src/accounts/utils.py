from src.supabase_client import supabase


def initialize_user_db(user_id, email):
      supabase.table("user").insert({
          "user_id": user_id,
          "email": email,
      }).execute()

