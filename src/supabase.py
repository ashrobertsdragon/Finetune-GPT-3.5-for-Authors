from decouple import config
from gotrue.types import AuthResponse, UserResponse
from supabase import create_client, Client

from .error_handling import email_admin
from .logging_config import LoggerManager


class SupabaseClient():
    _mono_state: dict = {}

    def _get_env_value(self, key: str) -> str:
        if isinstance(key, str):
            try:
                return config(key)
            except Exception:
                raise LookupError(f"Supabase API {key} not found")
        else:
            raise TypeError(f"{key} must be string")

    def __init__(self) -> None:
        self.__dict__ = self._mono_state
        self.error_logger = LoggerManager.get_error_logger()
        self.info_logger = LoggerManager.get_info_logger()

        try:
            self.url: str = self._get_env_value("SUPABASE_URL")
        except Exception:
            raise LookupError("Supabase API URL not found")
        
        if "default_client" not in self.__dict__:
            key: str = self._get_env_value("SUPABASE_KEY")
            self.default_client: Client = create_client(self.url, key)
            if self.default_client:
                self.log_info(
                    action="Initialized Supabase default client",
                    response={"Client initialized": "Default"}
                )

    def log_info(self, action: str, response, **kwargs) -> None:
        """
        Log a Supabase response with the info logger.

        Args:
            action (str): The action being performed.
            response (union): The response returned, typically data, a list of
                dictionaries and count=None.
            
        
        Example:
            log_info("select", {"email": "example@example.com", "name": "John"})
        
        """
        all_kwargs = ', '.join(f"{k}={v}" for k, v in kwargs.items())
        self.info_logger(f"{action} returned {response}{all_kwargs}")

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
            if arg_name == "file_content":
                arg_value = "text"
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

        self.error_logger(error_message)
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
            self.log_error(e, action, email=email)
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
            self.log_error(e, action, email=email)
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
            self.log_error(e, action)
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
            self.log_error(e, action, email=email)
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
            self.log_error(e, action, updates=updates)
            raise

class SupabaseStorage(SupabaseClient):

    def upload_file(self, bucket, upload_path, file_content, file_mimetype):
        action = "upload file"
        try:
            response = self.default_client.storage.from_(bucket).upload(
                path=upload_path,
                file=file_content,
                file_options={"content-type": file_mimetype}
            )
            print(response)
            return True
        except Exception as e:
            self.log_error(
                e, action, 
                upload_path=upload_path,
                file_content=file_content,
                file_mimetype=file_mimetype
            )
            return False
    
    def delete_file(self, bucket, file_path):
        action = "delete file"
        try:
            response = self.default_client.storage.from_(bucket).remove(file_path)
            print(response)
            return True
        except Exception as e:
            self.log_error(
                e, action, 
                file_path=file_path
            )
            return False
    
    def download_file(self, bucket:str, download_path:str, destination_path:str) -> bytes:
        action = "download file"
        try:
            with open(destination_path, 'wb+') as f:
                response = self.default_client.storage.from_(bucket).download(download_path)
                f.write(response)
        except Exception as e:
            self.log_error(
                e, action,
                download_path=download_path,
                destination_path=destination_path
            )
    
    def list_files(self, bucket:str) -> list:
        action = "list files"
        try:
            response = self.default_client.storage.from_(bucket).list()
            self.log_info(action, response)
            return response
        except Exception as e:
            self.log_error(e, action, bucket=bucket)
            return []

class SupabaseDB(SupabaseClient):
    def __init__(self) -> None:
        super().__init__()

        if "service_client" not in self.__dict__:
            service_role: str = super()._get_env_value("SUPABASE_SERVICE_ROLE")
            self.service_client: Client = create_client(self.url, service_role)
            if self.service_client:
                self.log_info(
                    action="Initialized Supabase service client",
                    response={"Client initialized": "service"}
                )
    
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
                if not isinstance(use_service_role, bool):
                    raise TypeError("use_service_role must be boolean")
                return self.service_client
            else:
                return self.default_client
        except Exception as e:
            action = "accessing client"
            self.log_error(e, action)
            return None
    
    def _validate_type(self, value:any, *, name:str, is_type:type):
        if not value:
            raise ValueError(f"{name} must have value")
        if not is_type:
            raise TypeError("is_type must not be None")
        if not isinstance(value, is_type):
            raise TypeError(f"{name} must be {is_type.__name__}")
    
    def _validate_string(self, value:any, name:str):
        self._validate_type(value, name=name, is_type=str)
    
    def _validate_dict(self, value:any, name:str):
        self._validate_type(value, name=name, is_type=dict)
    
    def _validate_table(self, value:any):
        self._validate_string(value, name="table_name")

    def insert_row(
        self, *, table_name: str, data: dict, use_service_role: bool = False
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
            ValueError: If the updates argument is not a dictionary, or
                table_name is not a string.
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
            self._validate_table(table_name)
            self._validate_dict(data, "data")
        except Exception as e:
            self.log_error(e, action, data=data, table_name=table_name)
        try:
            response = db_client.table(table_name).insert(data).execute()
            if not response.data:
                raise ValueError("Response has no data")
            else:
                self.log_info(action, response)
                return True
        except Exception as e:
            self.log_error(e, action, data=data, table_name=table_name)
            return False
    
    def select_row(
        self, *, table_name: str, match: dict, columns: list[str] = ["*"]
    ) -> dict:
        """
        Retrieves a row or columns from a table based on a matching condition.

        Args:
            table_name (str): The name of the table to retrieve the row from.
            match (dict): A dictionary representing the matching condition.
                The key should be the column name and the value should be 
                the corresponding value to match.
            ValueError: If the match argument is not a dictionary, or
                table_name is not a string.
            columns (list[str], optional): A list of column names to retrieve 
                from the row. Defaults to ["*"], which retrieves all columns.

        Returns:
            dict: A dictionary representing the retrieved row. If no row is
                found matching the condition, an empty dictionary is returned.

        Raises:
            ValueError: If the match argument is not a dictionary, or
                table_name is not a string.
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

        try:
            self._validate_table(table_name)
            self._validate_dict(match, "match")
            
        except ValueError as e:
            self.log_error(e, action, match=match, table_name=table_name)

        match_name, match_value = next(iter(match.items()))

        try:
            response = db_client.table(table_name) \
                .select(*columns) \
                .eq(match_name, match_value) \
                .execute()
            self.log_info(action, response)
            return response.data if response.data else {}
        except Exception as e:
            self.log_error(e, action, columns=columns, match=match)
            return {}
        
    def select_rows(
            self, *, table_name:str, matches:dict, columns:list[str]=["*"]
        ) -> list[dict]:
        """
        Selects rows from a table based on matching conditions.

        Args:
            table_name (str): The name of the table to select rows from.
            matches (dict): A dictionary representing the matching conditions.
                The keys should be column names and the values should be the 
                corresponding values to match.
            columns (list[str], optional): A list of column names to retrieve
                from the rows. Defaults to ["*"], which retrieves all columns.

        Returns:
            list[dict]: A list of dictionaries representing the selected rows.
                If no rows are found matching the conditions, an empty list is
                returned.

        Raises:
            ValueError: If the matches argument is not a dictionary or if any
                value in the matches dictionary is not a list, or if
                table_name is not a string.
            Exception: If there is an error while selecting the rows, an
                exception will be raised and logged.

        Example:
            supabase_db = SupabaseDB()
            result = supabase_db.select_rows(
                table_name="users",
                matches={"name": ["John Doe"], "age": [30, 40]},
                columns=["name", "age", "email"]
            )
        """
        db_client = self._select_client()
        action = "select"
        
        try:
            self._validate_table(table_name)
            self._validate_dict(matches, "match")
            for key, value in matches.items():
                if not isinstance(value, list):
                    raise ValueError(f"Value for filter '{key}' must be a list")
        except ValueError as e:
            self.log_error(e, action,matches=matches, table_name=table_name)

            
        try:
            response = db_client.table(table_name) \
                .select(*columns) \
                .in_(matches) \
                .execute()
            self.log_info(action, response)
            return response.data if response.data else [{}]
        except Exception as e:
            self.log_error(e, action, columns=columns, matches=matches)
            return [{}]

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
            ValueError: If the match argument is not a dictionary, or
                table_name is not a string.
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

        try:
            self._validate_table(table_name)
            self._validate_dict(match, "match")
            if len(match.keys()) != 1:
                raise ValueError("Match dictionary must have one key-value pair")
            for key, value in match.items():
                if not isinstance(key, str):
                    raise KeyError(f"{key} must be a string")
                if not isinstance(value, str):
                    raise KeyError(f"Value for filter '{key}' must be a string")
        except KeyError as e:
            self.log_error(e, action,match=match, table_name=table_name)

        match_name, match_value = next(iter(match.items()))
        try:
            res = db_client.table(table_name).update(info).eq(match_name, match_value).execute()
        except Exception as e:
            self.log_error(e, action, updates=info, match=match)
            return False
        if res.data:
            self.log_info(action, res)
            return True
        else:
            log="Data is the same"
            self.log_info(action, res, info=info, log=log)
            return False
        
    def find_row(self, *, table_name: str, match_column: str, within_period: int, columns: list[str] = ["*"]) -> dict:
        db_client = self._select_client()
        action = "find row"

        try:
            self._validate_table(table_name)
            self._validate_type(match_column, "str")
            self._validate_type(within_period, "int")
            self._validate_type(columns, "list")

            response = db_client.table(table_name).select(columns).lte(match_column, within_period).execute()
        except Exception as e:
            self.log_error(
                e, action,
                table_name=table_name,
                match_column=match_column,
                within_period=within_period,
                columns=columns
            )
            return {}
        
        if response and response.data:
            try:
                self._validate_dict(response.data)
                return response.data
            except Exception as e:
                self.log_error(
                    e, action,
                    table_name=table_name,
                    match_column=match_column,
                    within_period=within_period,
                    columns=columns
                )
                return {}

