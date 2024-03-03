import os

from google.cloud import storage

UPLOAD_FOLDER= None
DOWNLOAD_FOLDER = None


def initialize_constants():
    """
    Initializes the global constants for the application.
    """
    global DOWNLOAD_FOLDER
    global UPLOAD_FOLDER
    UPLOAD_FOLDER = initialize_upload_folder()
    DOWNLOAD_FOLDER = initialize_cloud_storage()
    return UPLOAD_FOLDER, DOWNLOAD_FOLDER

def initialize_upload_folder():
    """
    Determines if the environment is production or development and sets the path
    to the upload folder accordingly.
    """
    if os.environ.get("FLASK_ENV") == "production":
        UPLOAD_FOLDER = os.path.join("/tmp", "upload")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    else:
        UPLOAD_FOLDER = os.path.join("app", "upload_folder")
    return UPLOAD_FOLDER

def initialize_cloud_storage():
    """
    Initializes the Google Cloud Storage client.
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    storage_client = storage.Client()
    bucket_name = "finetuner_temp_files"
    bucket = storage_client.bucket(bucket_name)
    return bucket

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