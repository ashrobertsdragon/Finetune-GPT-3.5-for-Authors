from typing import Any, Callable, Optional, TypeAlias

from decouple import config
from gotrue.types import AuthResponse, UserResponse
from postgrest import APIResponse, SyncRequestBuilder
from pydantic import BaseModel
from supabase import Client, PostgrestAPIError, StorageException, create_client
from supabase._sync.client import SupabaseException

LogFunction: TypeAlias = Callable[[str, str, bool, Any, Any], None]
Table: TypeAlias = SyncRequestBuilder


class SupabaseLogin(BaseModel):
    url: str
    key: str
    service_role: str

    @classmethod
    def from_config(cls):
        return cls(
            url=config("SUPABASE_URL"),
            key=config("SUPABASE_KEY"),
            service_role=config("SUPABASE_SERVICE_ROLE"),
        )


def validate_response(
    value: Any,
    expected_type: type,
    allow_none: bool = False,
    name: str = "Response",
) -> None:
    """
    Validate that a response is of the expected type.

    Args:
        value: The value to validate.
        expected_type: The expected type of the value.
        name: The name of the value (for error messages).
        allow_none: Whether None is an allowed value.

    Raises:
        ValueError: If the value is None and allow_none is False.
        TypeError: If the value is not of the expected type.
    """
    if value is None:
        if not allow_none:
            raise ValueError(f"{name} must have a value")
        return

    if not isinstance(value, expected_type):
        raise TypeError(f"{name} must be of type {expected_type.__name__}")


class SupabaseClient:
    def __init__(
        self,
        supabase_login: SupabaseLogin,
        log_function: LogFunction,
    ):
        self.login = supabase_login
        self.log = log_function
        self.default_client: Client = self._initialize_client(
            self.login.url, self.login.key
        )
        self.service_client: Client = self._initialize_client(
            url=self.login.url, key=self.login.service_role
        )

    def _initialize_client(self, url: str, key: str) -> Client:
        try:
            return create_client(supabase_url=url, supabase_key=key)
        except SupabaseException as e:
            self.log(
                level="error",
                action="initialize client",
                exception=e,
            )

    def select_client(self, use_service_role: bool = False) -> Client:
        return self.service_client if use_service_role else self.default_client


class SupabaseAuth:
    def __init__(self, client: SupabaseClient, log_function: LogFunction):
        self.client: Client = client.client_class.select_client()
        self.log = log_function

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
            response: dict = self.client.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                }
            )
            validate_response(
                response, expected_type="Tuple", allow_none="response"
            )
            return response
        except Exception as e:
            self.log(level="error", action="signup", email=email, exception=e)
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
            return self.client.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )
        except Exception as e:
            self.log(level="error", action="login", email=email, exception=e)

    def sign_out(self) -> None:
        """
        Signs out the currently authenticated user.

        Raises:
            Exception: If an error occurs during the sign out process.

        Example:
            sign_out()
        """
        try:
            self.client.auth.sign_out()
        except Exception as e:
            self.log(level="error", action="logout", exception=e)
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
            self.client.auth.reset_password_email(
                email, options={"redirect_to": f"{domain}/reset-password.html"}
            )
        except Exception as e:
            self.log(level="error", action="reset_password", email=email, e=e)
            raise

    def update_user(self, updates: dict) -> UserResponse:
        """
        Updates a user with the provided updates.

        Args:
            updates (dict): A dictionary containing the updates to be made to
                the user.

        Raises:
            Exception: If an error occurs during the update process.

        Example:
            update_user(updates={"name": "John", "age": 30})
        """
        try:
            return self.client.auth.update_user(updates)
        except Exception as e:
            self.error(
                level="error",
                action="update user",
                updates=updates,
                exception=e,
            )
            raise


class SupabaseStorage:
    def __init__(
        self,
        client: SupabaseClient,
        log_function: LogFunction,
        validator: Callable[[Any, type, bool], None],
    ) -> None:
        self.client: Client = client.select_client()
        self.log = log_function
        self.validator = validator

    def _use_storage_connection(
        self, bucket: str, action: str, **kwargs
    ) -> Any:
        with self.client.storage.from_(bucket) as storage:
            return getattr(storage, action)(**kwargs)

    def _validate_response(
        self,
        response: Any,
        *,
        expected_type: type,
        action: str,
        bucket: str,
        **kwargs,
    ):
        try:
            self.validator(response, expected_type)
            return True
        except (ValueError, TypeError) as e:
            self.log(
                level="error",
                action=action,
                bucket=bucket,
                exception=e,
                **kwargs,
            )
            return False

    def upload_file(
        self,
        bucket: str,
        upload_path: str,
        file_content: bytes,
        file_mimetype: str,
    ) -> bool:
        try:
            self._use_storage_connection(
                bucket,
                "upload",
                path=upload_path,
                file=file_content,
                file_options={"content-type": file_mimetype},
            )
        except StorageException as e:
            self.log(
                level="error",
                action="upload file",
                bucket=bucket,
                upload_path=upload_path,
                file_content=file_content,
                file_mimetype=file_mimetype,
                exception=e,
            )
            return False
        return True

    def delete_file(self, bucket: str, file_path: str) -> bool:
        try:
            self._use_storage_connection(bucket, "remove", paths=[file_path])
        except StorageException as e:
            self.log(
                level="error",
                action="delete file",
                bucket=bucket,
                file_path=file_path,
                exception=e,
            )
            return False
        return True

    def download_file(
        self, bucket: str, download_path: str, destination_path: str
    ) -> None:
        try:
            with open(destination_path, "wb+") as f:
                response = self._use_storage_connection(
                    bucket, "download", path=download_path
                )
                f.write(response)
        except StorageException as e:
            self.log(
                level="error",
                action="download file",
                bucket=bucket,
                download_path=download_path,
                destination_path=destination_path,
                exception=e,
            )

    def list_files(
        self, bucket: str, folder: Optional[str] = None
    ) -> list[dict[str, str]]:
        action: str = "list files"
        try:
            if folder:
                response = self._use_storage_connection(
                    bucket, "list", path=folder
                )
            else:
                response = self._use_storage_connection(bucket, "list")
        except StorageException as e:
            self.log(level="error", action=action, bucket=bucket, exception=e)
            return []
        if self._validate_response(response, list, action, bucket):
            return response
        else:
            return []

    def create_signed_url(
        self,
        bucket: str,
        download_path: str,
        *,
        expires_in: Optional[int] = 3600,
    ) -> str:
        action = "create signed url"
        try:
            response = self._use_storage_connection(
                bucket,
                "create_signed_url",
                path=download_path,
                expires_in=expires_in,
            )
        except StorageException as e:
            self.log(
                level="error",
                action=action,
                bucket=bucket,
                download_path=download_path,
                expires_in=expires_in,
                exception=e,
            )
            return ""

        url = response["signedURL"]
        if self._validate_response(
            url,
            str,
            action,
            bucket,
            download_path=download_path,
            expires_in=expires_in,
        ):
            return url
        else:
            return ""


class SupabaseDB:
    def __init__(
        self,
        client: SupabaseClient,
        log_function: Callable[[str, str, bool, Any, Any], None],
        validator: Callable[[Any, type, bool], None],
    ) -> None:
        self.client = client
        self.log = log_function
        self.validator = validator
        self.empty_value: list[dict] = [{}]

    def _get_client(self, use_service_role: bool) -> Client:
        "Return the correct client based on the `use_service_role` boolean"
        return self.client.select_client(use_service_role)

    def _execute_query(
        self, db_client: Client, table_name: str, query: Callable
    ) -> APIResponse:
        """
        Execute the database query on the table with the correct client.

        Args:
            db_client (Client): The Supabase client with the correct
                permissions for the query.
            table_name (str): The name of the table to be queried.
            query (Callable): The lambda function of the Supabase SDK query.
                Example: `lambda table: table.insert(row_dictionary)`

        Returns:
            APIResponse: The json response object with a data list and count
                integer.
        """
        with db_client.from_(table_name) as table:
            return query(table).execute()

    def _validate_response(
        self,
        data: Any,
        *,
        action: str,
        table_name: str,
        **kwargs,
    ) -> bool:
        """
        Validate the data response from the Supabase SDK against the expected
        type and log an error if it doesn't match.

        Args:
            data (Any): The data object from the JSON response.
            action (str): The query action being performed.
            table_name (str): The table the query was performed on.
            **kwargs: Any other keyword arguments to be logged.

        Returns:
            bool: True if the data object is a list of dictionaries and False
                if not.
        """
        try:
            self.validator(data, list)
            for item in list:
                self.validator(item, dict)
            return True
        except (ValueError, TypeError) as e:
            self.log(
                level="error",
                action=action,
                table_name=table_name,
                exception=e,
                **kwargs,
            )
            return False

    def _get_filter(
        self, match: dict, action: str, table_name: str
    ) -> tuple[str, str]:
        """
        Parse the dictionary storing the query filter

        Args:
            match (dict): The dictionary containing the query filter.
            action (str): The query action being performed.
            table_name (str): The table the query is being performed on.

        Returns:
            tuple[str, str]: The match_name and match_value of the query
                filter.
        """
        try:
            if len(match.keys()) > 1:
                raise ValueError(
                    "Match dictionary must have one key-value pair"
                )
            for key, value in match.items():
                self.validator(key, str)
                try:
                    self.validator(value, str)
                except TypeError as error:
                    raise TypeError(
                        f"Value for filter '{key}' must be a string"
                    ) from error
        except (ValueError, TypeError) as e:
            self.log(
                level="error",
                exception=e,
                action=action,
                match=match,
                table_name=table_name,
            )

        match_name, match_value = next(iter(match.items()))
        return match_name, match_value

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
        """

        db_client: Client = self._get_client(use_service_role)
        try:
            response = self._execute_query(
                db_client=db_client,
                table_name=table_name,
                query=lambda table: table.insert(data),
            )
            if not response.data:
                raise ValueError("Response has no data")
        except (PostgrestAPIError, ValueError) as e:
            self.log(
                level="error",
                action="insert",
                data=data,
                table_name=table_name,
                exception=e,
            )
            return False
        return True

    def delete_row(self, *, table_name: str, match: dict) -> bool:
        """
        Deletes a row from a table based on a matching condition.
        Args:
            table_name (str): The name of the table to delete the row from.
            match (dict): A dictionary representing the matching condition for
                the row to delete. The keys should be the column name and the
                value should be the corresponding value to match.

        Returns:
            bool: True if the row deletion was successful, False otherwise.
        """
        action: str = "delete"
        db_client: Client = self._get_client(use_service_role=False)
        try:
            match_name, match_value = self._get_filter(
                match, action, table_name
            )
            self._execute_query(
                db_client=db_client,
                table_name=table_name,
                query=lambda table: table.delete.eq(match_name, match_value),
            )
            return True
        except (PostgrestAPIError, ValueError, TypeError) as e:
            self.log_error(e, action, match=match)
            return False

    def select_row(
        self,
        *,
        table_name: str,
        match: dict,
        columns: Optional[list[str]] = None,
    ) -> list[dict]:
        """
        Retrieves a row or columns from a table based on a matching condition.

        Args:
            table_name (str): The name of the table to retrieve the row from.
            match (dict): A dictionary representing the matching condition.
                The key should be the column name and the value should be
                the corresponding value to match.
            ValueError: If the match argument is not a dictionary, or
                table_name is not a string.
            columns (List[str], optional): A list of column names to retrieve
                from the row. Defaults to ["*"], which retrieves all columns.

        Returns:
            List[dict]: A list of dictionaries representing the retrieved row
                or rows. If no row is found matching the condition, an empty
                dictionary is returned.
        """
        action = "select"
        column_str = "*" if columns is None else ", ".join(columns)

        db_client: Client = self._get_client(use_service_role=True)
        try:
            match_name, match_value = self._get_filter(
                match, action, table_name
            )
            response = self._execute_query(
                db_client=db_client,
                table_name=table_name,
                query=lambda table: table.select(column_str).eq(
                    match_name, match_value
                ),
            )
            if not response or not response.data:
                raise ValueError("Response has no data")
        except (PostgrestAPIError, ValueError) as e:
            self.log(
                level="error",
                exception=e,
                action=action,
                table_name=table_name,
                column_str=column_str,
                match=match,
            )
            return self.empty_value
        if self._validate_response(
            response.data,
            expected_type=list,
            action=action,
            table_name=table_name,
            colum_str=column_str,
            match=match,
        ):
            return response.data
        else:
            return self.empty_value

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
        """
        action: str = "update"
        db_client: Client = self._get_client(use_service_role=False)
        try:
            match_name, match_value = self._get_filter(
                match, action, table_name
            )
            response = self._execute_query(
                db_client=db_client,
                table_name=table_name,
                query=lambda table: table.update(info).eq(
                    match_name, match_value
                ),
            )
        except (PostgrestAPIError, ValueError, TypeError) as e:
            self.log_error(e, action, updates=info, match=match)
            return False
        if response.data:
            return True
        log = "Data is the same"
        self.log(
            level="info",
            action=action,
            response=response.data,
            info=info,
            match=match,
            log=log,
        )
        return False

    def find_row(
        self,
        *,
        table_name: str,
        match_column: str,
        within_period: int,
        columns: Optional[list[str]],
    ) -> list[dict]:
        action: str = "find row"
        if columns is None:
            columns = ["*"]

        db_client: Client = self._get_client(use_service_role=False)
        try:
            response = self._execute_query(
                db_client=db_client,
                table_name=table_name,
                query=lambda table: table.select(columns).lte(
                    match_column, within_period
                ),
            )
        except PostgrestAPIError as e:
            self.log(
                level="error",
                exception=e,
                action=action,
                table_name=table_name,
                match_column=match_column,
                within_period=within_period,
                columns=columns,
            )
            return self.empty_value

        if (
            response
            and response.data  # noqa: W503
            and self._validate_response(  # noqa: W503
                response.data,
                expected_type=list,
                action=action,
                table_name=table_name,
                match_column=match_column,
                within_period=within_period,
                columns=columns,
            )
        ):
            return self.empty_value
