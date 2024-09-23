import io
from enum import Enum
from pathlib import Path

# import requests
from decouple import config

# from loguru import logger
# from requests.exceptions import RequestException
# from prosepal.exceptions import APIError
from prosepal.utils import random_str


class ChunkType(Enum):
    SLIDING_WINDOW_LARGE = "Sliding window - large"
    SLIDING_WINDOW_SMALL = "Sliding window - small"
    DIALOG_PROSE = "Dialog & prose"
    GENERATE_BEATS = "Generate beats"
    NONE = ""


def make_folder() -> tuple[Path, str]:
    """
    Generates a random string and creates a folder with that string in the
    upload folder. Returns the path to the folder and the random string.
    """
    temp_folder = random_str()
    folder_name = Path(config["UPLOAD_FOLDER"], temp_folder)
    try:
        folder_name.mkdir()
    except OSError:
        return make_folder()
    return folder_name, temp_folder


def is_encoding(file_path: Path, encoding: str) -> bool:
    """
    Checks if a file is encoded in a certain encoding.
    """
    try:
        with open(file_path, encoding=encoding) as f:
            f.read()
        return True
    except UnicodeDecodeError:
        return False


def is_valid_user_key(user_key) -> bool:
    return user_key.startswith("sk-") and 50 < len(user_key) < 60


def is_valid_file_size(file_path: Path) -> bool:
    file_size = file_path.__sizeof__()
    min_size, max_size = 1024, 1024 * 1024  # 1 KB, 1 MB
    return min_size <= file_size <= max_size


def call_api(api: str, file_path: Path, **kwargs) -> io.BytesIO:
    """
    Calls an API to send a file and return a file
    with open(file_path, "rb") as file:
        files = {"file": file}

        api_url = config(api)
        headers = kwargs.pop("headers", {})
        params = kwargs.pop("params", {})

        try:
            response = requests.post(
                api_url, files=files, headers=headers, params=params, **kwargs
            )
            response.raise_for_status()
        except RequestException as e:
            error_message = f"{api} experienced an error: {e}"
            logger.exception(error_message)
            raise APIError(error_message) from e

        file_content = response.content
        file_object = io.BytesIO(file_content)
        file_object.seek(0)
        return file_object
    """
    pass
