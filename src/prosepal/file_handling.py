from werkzeug.datastructures.file_storage import FileStorage

from .logging_config import LoggerManager
from .supabase import SupabaseStorage

storage = SupabaseStorage()
error_logger = LoggerManager.get_error_logger()


def send_file_to_bucket(
    user_folder: str, file: FileStorage, *, bucket: str
) -> str:
    """
    Uploads a file to a Supabase storage bucket.

    Args:
        user_folder (str): The user's uuid which acts as their folder name in
            the storage bucket where the file will be uploaded.
        file (FileStorage): The file to be uploaded, as a Flask FileStorage
        object.
        bucket (str): The name of the bucket to upload the file to. Must be
        specified as a keyword argument

    Returns:
        upload_path (str): The path the file in the storage bucket.

    Notes:
        - The file will be uploaded with the same name as the original file.
        - The file content type will be determined automatically based on the
        file's MIME type.
    """
    file_name = file.filename
    upload_path = f"{user_folder}/{file_name}"

    file_content = file.read()
    file_mimetype = file.content_type
    file.seek(0)
    deleted = False

    files = storage.list_files(bucket, user_folder)
    if any(file_name == file.get("name") for file in files):
        deleted = storage.delete_file(bucket, upload_path)
    if deleted or upload_path not in files:
        success = storage.upload_file(
            bucket, upload_path, file_content, file_mimetype
        )

    if not success:
        error_logger(f"{file_name} not uploaded")
    return upload_path


def create_signed_url(bucket: str, download_path: str) -> str:
    """
    Creates a signed URL for a file in the specified bucket.

    Args:
        bucket (str): The name of the Supabase bucket the file is stored in.
        download_path(str): The combined folder name (user auth id) and
            filename of the file to be downloaded.

    Returns:
        url (str): The signed url of the file to be downloaded or an empty
            string if the method returned an empty string.

    """
    url = storage.create_signed_url(bucket, download_path)
    return url if url else ""
