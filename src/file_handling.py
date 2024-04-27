from .supabase import SupabaseStorage

 
storage = SupabaseStorage()

def upload_supabase_bucket(user_folder, file, *, bucket):
    """
    Uploads a file to a Supabase storage bucket.

    Args:
        user_folder (str): The user's uuid which acts as their folder name in the 
        storage bucket where the file will be uploaded.
        file (FileStorage): The file to be uploaded, as a Flask FileStorage
        object.
        bucket (str): The name of the bucket to upload the file to. Must be
        specified as a keyword argument

    Returns:
        upload_path (str): The path the file in the storage bucket.

    Raises:
        Exception: If an error occurs during the file upload.

    Notes:
        - The file will be uploaded with the same name as the original file.
        - The file content type will be determined automatically based on the
        file's MIME type.
        - If the file upload is successful, a success flash message will be
        displayed.
        - If the file upload fails, an error flash message will be displayed.
        - Any exceptions that occur during the file upload will be logged and
        an error flash message will be displayed.
    """

    file_name = file.filename
    upload_path = f"{user_folder}/{file_name}"

    file_content = file.read()
    file_mimetype = file.content_type
    file.seek(0)

    storage.upload_file(bucket, upload_path, file_content, file_mimetype)

    return upload_path