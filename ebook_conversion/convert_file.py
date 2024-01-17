import os

from ebook_conversion.docx_conversion import read_docx
from ebook_conversion.epub_conversion import read_epub
from ebook_conversion.pdf_conversion import read_pdf
from ebook_conversion.text_conversion import parse_text_file
from file_handling import read_text_file, write_to_file

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
    raise ValueError("Invalid file type")

  book_name = f"{base_name}.txt"
  book_path = os.path.join(folder, book_name)
  write_to_file(book_content, book_path)
  return book_name
