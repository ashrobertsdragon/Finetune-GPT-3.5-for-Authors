import os

from google.oauth2 import service_account
from google.cloud import storage

class FileStorageHandler:
    def __init__(self):
        self._upload_folder = self._set_upload_folder()
        self._download_folder = self._initialize_cloud_storage()
    
    @property
    def upload_folder(self):
        return self._upload_folder
    
    @property
    def download_folder(self):
        return self._download_folder
    
    def _get_storage_account_credentials(self):
        """
        Returns the service account credentials based on the FLASK_ENV 
        environment variable.
        """
        env = os.environ.get("FLASK_ENV")
        if env == "staging":
            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_STAGING")
        else:
            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

        return service_account.Credentials.from_service_account_file(credentials_path)
    
    def _initialize_cloud_storage(self):
        """
        Initializes the Google Cloud Storage client.
        """
        storage_client = storage.Client(credentials=get_service_account_credentials())
        bucket_name = "finetuner_temp_files"
        bucket = storage_client.bucket(bucket_name)
        return bucket

    def _set_upload_folder(self):
        """
        Determines the environment and sets the path to the upload folder accordingly.
        """
        if os.environ.get("FLASK_ENV") in ["production", "staging"]:
            upload_folder = os.path.join("/tmp", "upload")
            os.makedirs(upload_folder, exist_ok=True)
        else:
            upload_folder = os.path.join("src", "upload_folder")
        return upload_folder

    def write_to_gcs(self, content: str, file_name: str):
        """
        Writes a text file to a Google Cloud Storage file.
        """
        blob = self._download_folder.blob(file_name)
        blob.upload_from_string(content, content_type="text/plain")

    def upload_file_to_gcs(self, file_path: str, gcs_file_name: str):
        """
        Uploads a file to a Google Cloud Storage bucket.
        """
        blob = self._download_folder.blob(gcs_file_name)
        with open(file_path, "rb") as file_obj:
            blob.upload_from_file(file_obj)
