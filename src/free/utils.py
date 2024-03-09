import os

from src import app
from src.utils import random_str

def make_folder() -> tuple[str, str]:
    """
    Generates a random string and creates a folder with that string in the upload
    folder. Returns the path to the folder and the random string.
    """
    temp_folder = random_str()
    folder_name = os.path.join(app.config["UPLOAD_FOLDER"], temp_folder)
    try:
        os.makedirs(folder_name)
    except OSError:
        return make_folder()
    return folder_name, temp_folder

def is_encoding(file_path: str, encoding: str) -> bool:
    """
    Checks if a file is encoded in a certain encoding.
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            f.read()
        return True
    except UnicodeDecodeError:
        return False
