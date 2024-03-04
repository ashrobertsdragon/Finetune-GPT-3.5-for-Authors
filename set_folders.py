import os

from google.oauth2 import service_account
from google.cloud import storage

# Constants
UPLOAD_FOLDER= None
DOWNLOAD_FOLDER = None


def set_upload_folder():
    """
    Determines the environment and sets the path to the upload folder accordingly.
    """
    if os.environ.get("FLASK_ENV") in ["production", "staging"]:
        UPLOAD_FOLDER = os.path.join("/tmp", "upload")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    else:
        UPLOAD_FOLDER = os.path.join("src", "flask_app", "upload_folder")
    return UPLOAD_FOLDER

def get_service_account_credentials():
    """
    Returns the service account credentials based on the FLASK_ENV environment
    variable.
    """
    env = os.environ.get("FLASK_ENV")
    if env == "staging":
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_STAGING")
    else:
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    return service_account.Credentials.from_service_account_file(credentials_path)

def initialize_cloud_storage():
    """
    Initializes the Google Cloud Storage client.
    """
    storage_client = storage.Client(credentials=get_service_account_credentials())
    bucket_name = "finetuner_temp_files"
    bucket = storage_client.bucket(bucket_name)
    return bucket

def set_constants():
    """
    Initializes the global constants for the application.
    """
    global DOWNLOAD_FOLDER
    global UPLOAD_FOLDER
    UPLOAD_FOLDER = set_upload_folder()
    DOWNLOAD_FOLDER = initialize_cloud_storage()
    return UPLOAD_FOLDER, DOWNLOAD_FOLDER

# Getters
def get_upload_folder() -> str:
    """
    Returns the upload folder.
    """
    return UPLOAD_FOLDER

def get_download_folder() -> str:
    """
    Returns the download folder.
    """
    return DOWNLOAD_FOLDER
