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
    
    def _select_client(self, use_service_role: bool = False) -> Client:
        """
        Selects the appropriate Supabase client.

        Args:
            use_service_role (bool, optional): Determines whether to use the 
                service role client or the default client. Defaults to False.

        Returns:
            Client: The selected Supabase client.
        """
        try:
            if use_service_role:
                return self.service_client
            else:
                return self.default_client
        except Exception as e:
            email_admin(f"Error {e} accessing client.")
            return None
    
    def _check_table(self, table_name: str, action: str, **kwargs) -> bool:
        """
        Checks if a table exists in the database, and logs error (inside
        email_admin function) if it does not.

        Args:
            table_name (str): The name of the table to check.
            action (str): The verb representing the intended SQL operation 
                (e.g., "SELECT", "INSERT", "UPDATE", "DELETE").
            **kwargs (dict, optional): Additional keyword arguments specific 
                to the intended SQL operation. Can include column names, 
                data values, etc., depending on the context.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        db_client = self._select_client(use_service_role=True)
        if not db_client.table(table_name).exists():
            table_error = f"Error: No table {table_name}."
            message = f"{table_error} Cannot {action} {kwargs}."
            email_admin(message)
            return False
        return True
    
    def insert_row(
        self, table_name: str, *, data: dict, use_service_role: bool = False
    ) -> bool:
        """
        Inserts a row into a table.

        Args:
            table_name (str): The name of the table to insert the row into.
            data (dict): The data to be inserted as a row. Should be a 
                dictionary where the keys represent the column names and the 
                values represent the corresponding values for each column.
            use_service_role (bool, optional): Determines whether to use the 
              service role client or the default client. Service role client
              should only be used for operations where a new user row is being
              inserted. Otherwise use default client for RLS policy on
              authenticated user. Defaults to False.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            Exception: If there is an error while inserting the row, an 
                exception will be raised and logged.

        Example:
            supabase_db = SupabaseDB()
            supabase_db.insert_row(
                table_name="users",
                data={
                    "name": "John Doe",
                    "age": 30,
                    "email": "johndoe@example.com"
                },
                use_service_role=True
            )
        """
        db_client = self._select_client(use_service_role)
        if not self._check_table(table_name, action="insert", data=data):
            return False
        try:
            db_client.table(table_name).insert(data).execute()
            return True
        except Exception as e:
            email_admin(f"Error {e} saving {data} to {table_name}")
            return False
    
    def select_row(
        self, table_name: str, *, match: dict, columns: list[str] = ["*"]
    ) -> dict:
        """
        Retrieves a row or columns from a table based on a matching condition.

        Args:
            table_name (str): The name of the table to retrieve the row from.
            match (dict): A dictionary representing the matching condition.
                The keys should be the column names and the values should be 
                the corresponding values to match.
            columns (list[str], optional): A list of column names to retrieve 
                from the row. Defaults to ["*"], which retrieves all columns.

        Returns:
            dict: A dictionary representing the retrieved row. If no row is
                found matching the condition, an empty dictionary is returned.

        Raises:
            Exception: If there is an error while retrieving the row, an
                exception will be raised and logged.

        Example:
            supabase_db = SupabaseDB()
            result = supabase_db.select_row(
                table_name="users",
                match={"name": "John Doe"},
                columns=["name", "age", "email"]
            )
            print(result)
            # Output: {"name": "John Doe", "age": 30, "email": "johndoe@example.com"}
        """
        db_client = self._select_client()
        
        if not self._check_table(
            table_name,
            action="select",
            columns=columns,
            match=match,
        ):
            return
        try:
            response = db_client.table(table_name) \
                .select(*columns).eq(**match).execute()
            return response.data if response.data else {}
        except Exception as e:
            email_admin(f"Error {e} retrieving {columns} for {match}")

    def update_row(self, table_name: str, info: dict, *, match: dict) -> bool:
        """
        Updates a row in the table with data when the row matches a column.
        Returns True if the update was successful, False otherwise.

        Args:
            table_name (str): The name of the table to update the row in.
            info (dict): A dictionary representing the data to update in the
                row. The keys should be the column names and the values should
                be the corresponding values to update.
            match (dict): A dictionary representing the matching condition for
                the row to update. The keys should be the column names and the
                values should be the corresponding values to match.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            Exception: If there is an error while updating the row, an
                exception will be raised and logged.

        Example:
            supabase_db = SupabaseDB()
            result = supabase_db.update_row(
                table_name="users",
                info={"age": 31},
                match={"name": "John Doe"}
            )
            print(result)
            # Output: True
        """
        db_client = self._select_client()
        if not self._check_table(
            table_name,
            action="update",
            info=info,
            match=match
        ):
            return False
        try:
            db_client.table(table_name).update(info).eq(**match).execute()
            return True
        except Exception as e:
            email_admin(f"Error {e}\n updating {info} for {match}")
            return False
