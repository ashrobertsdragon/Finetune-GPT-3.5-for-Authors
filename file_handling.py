import json
import os
import secrets
import string

from set_folders import FileStorageHandler

folders = FileStorageHandler()

# Folder related functions
def random_str():
    return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))

def make_folder() -> tuple[str, str]:
    """
    Generates a random string and creates a folder with that string in the upload
    folder. Returns the path to the folder and the random string.
    """
    temp_folder = random_str()
    folder_name = os.path.join(folders.upload_folder, temp_folder)
    try:
        os.makedirs(folder_name)
    except OSError:
        return make_folder()
    return folder_name, temp_folder

# Encoding related functions
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

# File related functions
def read_text_file(file_path: str) -> str:
    "Reads a text file and returns its content."
    with open(file_path, "r") as f:
        read_file = f.read()
    return read_file

def write_jsonl_file(content: list, file_path: str):
    "Writes a list of dictionaries to a JSONL file"
    with open(file_path, "a") as f:
        for item in content:
            json.dump(item, f)
            f.write("\n")
