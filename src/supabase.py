import logging

from decouple import config
from gotrue.types import AuthResponse, UserResponse
from supabase import create_client, Client

from .error_handling import email_admin


error_logger = logging.getLogger("error_logger")
info_logger = logging.getLogger("info_logger")

class SupabaseClient():
    _mono_state: dict = {}

    def __init__(self) -> None:
        self.__dict__ = self._mono_state

        self.url: str = config("SUPABASE_URL")
        
        if "default_client" not in self.__dict__:
            key: str = config("SUPABASE_KEY")
            self.default_client: Client = create_client(self.url, key)
    
    def log_info(self, action: str, response: dict) -> None:
        """
        Log a Supabase response with the info logger.

        Args:
            action (str): The action being performed.
            response (dict): The dictionary of table data returned.
        
        Example:
            log_info("select", {"email": "example@example.com", "name": "John"})
        
        """
        info_logger.info(f"{action} returned {response}")

    def create_error_message(self, action: str, **kwargs) -> str:
        """
        Create the error message for for logging errors.

        Args:
            action (str): The action being performed.
            updates (dict, optional): The updates being made. Defaults to
                None.
            match (dict, optional): The matching criteria. Defaults to None.
            email (str, optional): The email associated with the error.
                Defaults to None.
            table_name (str, optional): The name of the table. Defaults to 
                None.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The error message.

        Example:
            create_error_message(
                "insert", updates={"name": "John"}, table_name="users"
            )
        """
        error_message: list = [f"Error performing {action}"]

        arguments = {**kwargs}
        for arg_name, arg_value in arguments.items():
            if arg_value:
                error_message.append(f" with {arg_name}: {arg_value}")

        return " ".join(error_message)

    def log_error(self, e: Exception, action: str, **kwargs) -> None:
        """
        Log an error and send an email to the admin.

        Args:
            e (Exception): The exception that occurred.
            action (str): The action being performed.
            **kwargs: Additional keyword arguments.

        Returns:
            None

        Example:
            log_error(
                Exception("Something went wrong"), "insert",
                updates={"name": "John"}, table_name="users"
            )
        """
        error_message = self.create_error_message(action, **kwargs)

        error_message += f"\nException: {str(e)}"

        error_logger.error(error_message)
        self.send_email_admin(error_message)

    def send_email_admin(self, error_message) -> None:
        email_admin(error_message)

class SupabaseAuth(SupabaseClient):
    def __init__(self) -> None:
        super().__init__()
    def sign_up(self, *, email: str, password: str) -> AuthResponse:
        """
        Signs up a user with the provided email and password.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            AuthResponse: The response object containing the authentication
                information.

        Raises:
            Exception: If an error occurs during the sign up process.

        Example:
            sign_up(email="example@example.com", password="password123")
        """
        try:
            response = self.default_client.auth.sign_up({
                "email": email,
                "password": password,
            })
            return response
        except Exception as e:
            action = "signup"
            super().log_error(e, action, email=email)
            raise

    def sign_in(self, *, email: str, password: str) -> AuthResponse:
        """
        Signs in a user with the provided email and password.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            AuthResponse: The response object containing the authentication
                information.

        Raises:
            Exception: If an error occurs during the sign in process.

        Example:
            sign_in(email="example@example.com", password="password123")
        """
        try:
            data = self.default_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return data
        except Exception as e:
            action = "login"
            super().log_error(e, action, email=email)
            raise

    def sign_out(self) -> None:
        """
        Signs out the currently authenticated user.

        Raises:
            Exception: If an error occurs during the sign out process.

        Example:
            sign_out()
        """
        try:
            self.default_client.auth.sign_out()
        except Exception as e:
            action = "logout"
            super().log_error(e, action)
            raise

    def reset_password(self, *, email: str, domain: str) -> None:
        """
        Resets the password for a user with the provided email.

        Args:
            email (str): The email of the user.
            domain (str): The domain of the application.

        Raises:
            Exception: If an error occurs during the password reset process.

        Example:
            reset_password(email="example@example.com", domain="example.com")
        """
        try:
            self.default_client.auth.reset_password_email(
                email,
                options={"redirect_to": f"{domain}/reset-password.html"}
            )
        except Exception as e:
            action = "reset_password"
            super().log_error(e, action, email=email)
            raise

    def update_user(self, updates: dict) -> UserResponse:
        """
        Updates a user with the provided updates.

        Args:
            updates (dict): A dictionary containing the updates to be made to
                the user.

        Returns:
            UserResponse: The response object containing the updated user
                information.

        Raises:
            Exception: If an error occurs during the update process.

        Example:
            update_user(updates={"name": "John", "age": 30})
        """
        try:
            data = self.default_client.auth.update_user(updates)
            return data
        except Exception as e:
            action = "update user"
            super().log_error(e, action, updates=updates)
            raise

class SupabaseStorage(SupabaseClient):
    def upload_file(self, bucket, upload_path, file_content, file_mimetype):
        try:
            self.default_client.storage.from_(bucket).upload(
                path=upload_path,
                file=file_content,
                file_options={"content-type": file_mimetype}
            )
        except Exception as e:
            action = "upload file"
            super().log_error(
                e, action, 
                upload_path=upload_path,
                file_content=file_content,
                file_mimetype=file_mimetype
            )

class SupabaseDB(SupabaseClient):
    def __init__(self) -> None:
        super().__init__()

        if "service_client" not in self.__dict__:
            service_role: str = config("SUPABASE_SERVICE_ROLE")
            self.service_client: Client = create_client(self.url, service_role)
    
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
            action = "accessing client"
            super().log_error(e, action)
            return None
    
    
    def insert_row(
        self, *, table_name: str, updates: dict, use_service_role: bool = False
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
        action = "insert"
        try:
            response = db_client.table(table_name).insert(updates).execute()
            super().log_info(action, response)
            return True
        except Exception as e:
            super().log_error(e, action, updates=updates, table_name=table_name)
            return False
    
    def select_row(
        self, *, table_name: str, match: dict, columns: list[str] = ["*"]
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
        action = "select"
        match_name, match_value = next(iter(match.items()))

        try:
            response = db_client.table(table_name) \
                .select(*columns).eq(match_name, match_value).execute()
            super().log_info(action, response)
            return response.data if response.data else {}
        except Exception as e:
            super().log_error(e, action, columns=columns, match=match)
            return {}

    def update_row(self, *, table_name: str, info: dict, match: dict) -> bool:
        """
        Updates a row in the table with data when the row matches a column.
        Returns True if the update was successful, False otherwise.

        Args:
            table_name (str): The name of the table to update the row in.
            info (dict): A dictionary representing the data to update in the
                row. The keys should be the column names and the values should
                be the corresponding values to update.
            match (dict): A dictionary representing the matching condition for
                the row to update. The keys should be the column name and the
                value should be the corresponding value to match.

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
        action = "update"
        match_name, match_value = next(iter(match.items()))
        try:
            response = db_client.table(table_name).update(info) \
                .eq(match_name, match_value).execute()
            super().log_info(action, response)
            return True
        except Exception as e:
            super().log_error(e, action, updates=info, match=match)
            return False
