from src.supabase_client import supabase


def add_extra_user_info(user_id, email):
      supabase.table("userTable").insert({
          "user_id": user_id,
          "email": email,
      }).execute()

