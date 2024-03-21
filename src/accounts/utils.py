from src.supabase import supabase 


def initialize_user_db(auth_id, email):
      supabase.table("user").insert({
          "auth_id": auth_id,
          "email": email,
      }).execute()

