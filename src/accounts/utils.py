from src.supabase import supa_service


def initialize_user_db(auth_id, email):
      supa_service.table("user").insert({
          "auth_id": auth_id,
          "email": email,
      }).execute()

