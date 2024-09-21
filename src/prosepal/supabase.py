from typing import Any, Callable, Optional, ParamSpec, TypeVar

from decouple import config
from gotrue.types import AuthResponse, UserResponse
from loguru import logger
from pydantic import BaseModel
from supabase import Client, StorageException, create_client
from supabase._sync.client import SupabaseException

T = TypeVar("T")
P = ParamSpec("P")

LogFunctionType = Callable[[str, str, bool, Any, Any], None]


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
    response: Any, expected_type: type, allow_none: bool = False
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
    if response is None:
        if not allow_none:
            raise ValueError("response must have a value")
        return

    if not isinstance(response, expected_type):
        raise TypeError(f"response must be of type {expected_type.__name__}")


class SupabaseClient:
    def __init__(
        self,
        supabase_login: SupabaseLogin,
        log_function: LogFunctionType,
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
    def __init__(self, client: SupabaseClient, log_function: LogFunctionType):
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
        log_function: LogFunctionType,
        validator: Callable[[Any, type, bool], None],
    ) -> None:
        self.client: Client = client.select_client()
        self.log = log_function
        self.validator = validator

    def _use_storage_connection(
        self, bucket: str, action: str, **kwargs
    ) -> Any:
        with self.client.storage.from_(bucket) as storage_client:
            return getattr(storage_client, action)(**kwargs)

    def _validate_response(
        self,
        response: Any,
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

        try:
            response = db_client.table(table_name).insert(data).execute()
            if not response.data:
                raise ValueError("Response has no data")
        except Exception as e:
            self.log_error(
                e, action="insert", data=data, table_name=table_name
            )
            return False
        return True

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
        """
        db_client = self._select_client(use_service_role=True)

        match_name, match_value = next(iter(match.items()))
        column_str = "*" if columns is None else ", ".join(columns)
        try:
            if len(match) > 1:
                raise ValueError(
                    "Match dictionary should have only one key-value pair"
                )
            response = (
                db_client.table(table_name)
                .select(column_str)
                .eq(match_name, match_value)
                .execute()
            )
            logger.debug(response)
            if not response or not response.data:
                raise ValueError("Response has no data")

            if isinstance(response.data, list):
                return response.data
            else:
                raise TypeError("Returned data was not a list")
        except Exception as e:
            self.log_error(
                e,
                action="select",
                table_name=table_name,
                column_str=column_str,
                match=match,
            )
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
        action: str = "update"

        try:
            if len(match.keys()) != 1:
                raise ValueError(
                    "Match dictionary must have one key-value pair"
                )
            for key, value in match.items():
                if not isinstance(key, str):
                    raise KeyError(f"{key} must be a string")
                if not isinstance(value, str):
                    raise KeyError(
                        f"Value for filter '{key}' must be a string"
                    )
        except KeyError as e:
            self.log_error(e, action, match=match, table_name=table_name)

        match_name, match_value = next(iter(match.items()))
        try:
            res = (
                db_client.table(table_name)
                .update(info)
                .eq(match_name, match_value)
                .execute()
            )
        except Exception as e:
            self.log_error(e, action, updates=info, match=match)
            return False
        if res.data:
            return True
        log = "Data is the same"
        self.log_info(action, res, info=info, log=log)
        return False

    def find_row(
        self,
        *,
        table_name: str,
        match_column: str,
        within_period: int,
        columns: Optional[list[str]],
    ) -> dict:
        db_client = self._select_client()
        action: str = "find row"
        if columns is None:
            columns = ["*"]
        try:
            response = (
                db_client.table(table_name)
                .select(columns)
                .lte(match_column, within_period)
                .execute()
            )
        except Exception as e:
            self.log_error(
                e,
                action,
                table_name=table_name,
                match_column=match_column,
                within_period=within_period,
                columns=columns,
            )
            return {}

        if response and response.data:
            try:
                self._validate_dict(response.data)
                return response.data
            except Exception as e:
                self.log_error(
                    e,
                    action,
                    table_name=table_name,
                    match_column=match_column,
                    within_period=within_period,
                    columns=columns,
                )
                return {}
