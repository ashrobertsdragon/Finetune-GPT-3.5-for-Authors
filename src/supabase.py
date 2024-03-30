from decouple import config

from supabase import create_client, Client
from .error_handling import email_admin

class SupabaseDB():
    def __init__(self) -> None:
        url: str = config("SUPABASE_URL")
        key: str = config("SUPABASE_KEY")
        service_role: str = config("SUPABASE_SERVICE_ROLE")

        self.default_client: Client = create_client(url, key)
        self.service_client: Client = create_client(url, service_role)
    
    def _get_client(self, use_service_role: bool = False) -> Client:
        """Selects the appropriate Supabase client."""
        return self.service_client if use_service_role else self.default_client
    
    def insert_row(
        self, table_name: str, *, data: dict, use_service_role: bool = False
    ) -> None:
        """Inserts a row into a table.
        """
        db_client = self._get_client(use_service_role)
        try:
            data = db_client.table(table_name).insert(data).execute()
        except Exception as e:
            email_admin(f"Error {e} saving {data} to {table_name}")
    
    def select_row(
        self, table_name: str, *, match: dict, columns: list[str] = ["*"]
    ) -> dict:
        """
        Retrieves a rowor columns from a row from a table based on a matching
        condition.
        """
        db_client = self.default_client
        (match_column, match_value), = match.items()
        try:
            response = db_client.table(table_name) \
                .select(*columns).eq(match_column, match_value).execute()
            return response.data if response.data else {}
        except Exception as e:
            email_admin(f"Error {e} retrieving {columns} for {match}")

    def update_row(self, table_name: str, data, *, match: dict) -> None:
        """
        Updates a row in the table with data when the row matches a column.
        """

        db_client = self.default_client
        (match_column, match_value), = match.items()
        try:
            data = db_client.table(table_name) \
                .update(data).eq(match_column, match_value).execute()
        except Exception as e:
            email_admin(f"Error {e}\n updating {data} for {match_value}")
