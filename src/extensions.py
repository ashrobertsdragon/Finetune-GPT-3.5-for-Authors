from bcrypt import Bcrypt
from supabase_client import get_supabase

bcrypt = Bcrypt()
db = get_supabase()