import logging
import os

from ebook_conversion.docx_conversion import read_docx
from ebook_conversion.epub_conversion import read_epub
from ebook_conversion.pdf_conversion import read_pdf
from ebook_conversion.text_conversion import parse_text_file
from file_handling import read_text_file
from set_folders import FileStorageHandler

folders = FileStorageHandler()


error_logger = logging.getLogger("error_logger")

def convert_file(file_path: str, metadata: dict) -> None:
    """
    Converts a book to a text file with 3 asterisks for chapter breaks
    Arguments:
        book_name: Name of the book.
        folder_name: Name of the folder containing the book.
    """

    book_content = ""
    folder, book_file = os.path.split(file_path)

    book_file = book_file.replace(" ", "_")
    book_file = book_file.replace("-", "_")
    filename_list = book_file.split(".")

    if len(filename_list) > 1:
        base_name = "_".join(filename_list[:-1])
    else:
        base_name = filename_list[0]
    extension = filename_list[-1].lower()

    if extension == "epub":
        book_content = read_epub(file_path, metadata)
    elif extension == "docx":
        book_content = read_docx(file_path, metadata)
    elif extension == "pdf":
        book_content = read_pdf(file_path, metadata)
    elif extension == "txt" or extension == "text":
        book_content = read_text_file(file_path)
        book_content = parse_text_file(book_content)
    else:
        error_logger.error("Invalid file type")

    book_name = f"{base_name}.txt"
    pseudopath=f"{folder}/{book_name}"
    folders.write_to_gcs(book_content, pseudopath)
    return book_name, pseudopath

