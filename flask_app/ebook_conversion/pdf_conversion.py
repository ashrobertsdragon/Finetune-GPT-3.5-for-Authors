import base64
import logging
import re
from io import BytesIO
from typing import Any, Tuple

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1
from pdfminer.pdftypes import PDFStream
from pdfminer.layout import LTChar, LTContainer, LTText
from pdfminer.high_level import extract_pages
from PIL import Image

from ebook_conversion.chapter_check import is_chapter, is_not_chapter, CHAPTER_MARKER
from ebook_conversion.ocr import run_ocr
from ebook_conversion.text_conversion import desmarten_text


error_logger = logging.getLogger("error_logger")
info_logger = logging.getLogger("info_logger")

END_PARAGRAPH = ('.', '!', '?', '."', '!"', '?"')

def create_image_from_binary(binary_data, width: int, height: int) -> str:
        """
        Create an image from binary data.

        Arguments:
                binary_data (bytes): The binary data of the image.
                width (int): The width of the image.
                height (int): The height of the image.

        Returns str: The string representation of the image.
        """

        try:
                image = Image.frombytes('1', (width, height), binary_data)
                image = image.convert('L')
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                image = base64.b64encode(buffered.getvalue()).decode('utf-8')
                return image
        except Exception as e:
                error_logger.exception(f"failed to create base64 encoded image due to {e}")

def extract_image(document: bytes, obj_num: int, attempt: int) -> str:
        """
        Convert binary image data into a base64-encoded JPEG string.

        This function takes binary data of an image, along with its width and 
        height, and converts it into a base64-encoded JPEG format string. This is 
        useful for encoding images in a format that can be easily transmitted or 
        stored.

        Arguments:
                binary_data (bytes): The binary data of the image.
                width (int): The width of the image in pixels.
                height (int): The height of the image in pixels.

        Returns str: A base64-encoded string representing the JPEG image.

        Raises:
                Exception: If there is an error in processing the image data.
        """

        if attempt > 1:
                return None
        try:
                obj = resolve1(document.getobj(obj_num))
                if obj and isinstance(obj, PDFStream):
                        width = obj["Width"]
                        height = obj["Height"]
                        if width < 5 or height < 5:
                                raise Exception("Image too small. Not target image")
                        if width > 1000 and height > 1000:
                                raise Exception("probably full page image")
                        stream = obj.get_data()
                        return create_image_from_binary(stream, width, height)
        except Exception as e:
                info_logger.info(f"Issue: {e} with object: {obj_num}")
                return extract_image(document, obj_num + 1, attempt + 1)

def parse_img_obj(file_path: str, obj_nums: list) -> str:
        """
        Extracts and processes images from a PDF file, then performs OCR to convert
        images to text.

        This function takes the path of a PDF file and a list of object numbers
        (obj_nums) which are potential image objects within the PDF. It attempts 
        to extract images from these objects and then uses OCR to convert these 
        images into text. The text from all images is concatenated and returned 
        as a single string.

        Arguments:
                file_path (str): The file path to the PDF from which to extract images.
                obj_nums (list): A list of object numbers in the PDF that potentially
                contain images.

        Returns text (str): the concatenated text extracted from all images.
        """

        with open(file_path, 'rb') as f:
                parser = PDFParser(f)
                document = PDFDocument(parser)
                base64_images = []
                for obj_num in obj_nums:
                        image = extract_image(document, obj_num, attempt = 0)
                        base64_images.append(image) if image else None
        text = run_ocr(base64_images) if base64_images else ""
        return text

def process_element(element: Any) -> Tuple[str, Any]:
        """
        Processes a PDF layout element to identify its type and extract relevant
        data.

        This function categorizes a given PDF layout element into types such as
        image, text, or other. For image elements, it returns the object ID. For
        text elements, it returns the extracted text. The function handles
        container elements by recursively processing their children. If an element
        does not match any specific type, it is categorized as "other".

        Arguments:
                element (Any): A PDF layout element from pdfminer.

        Returns: A tuple containing the element type and its relevant data (object
                ID for images or text content for text elements), or None for other types.
        """

        if hasattr(element, "stream"):
                return ("image", element.stream.objid)
        elif isinstance(element, LTText) and not isinstance(element, LTChar):
                return ("text", element.get_text())
        elif isinstance(element, LTContainer):
                for child in element:
                        return process_element(child)
        return ("other", None)

def parse_pdf_page(page: str, metadata: dict) -> str:
        """
        Parses the given pdf page and returns it as a string.
        Arguments:
                page: A pdf page.
        Returns the pdf page as a string.
        """
        print("entering function")
        
        def remove_extra_spaces(line: str) -> str:
                "Remove extra spaces in middle of string"
                return " ".join(line.split())

        def concatenate_paragraph(paragraph_list: list) -> str:
                "Concatenate lines of paragraph after extra spaces removed"
                return " ".join(remove_extra_spaces(line) for line in paragraph_list)

        def is_end_of_paragraph(paragraph_list: list) -> bool:
                "Check if previous line was end of paragraph"
                return paragraph_list[-1].rstrip().endswith(END_PARAGRAPH)

        def check_beginning_of_page(text_lines: int, metadata: dict, line: str) -> Tuple[int, str]:
                """
                Checks line at beginning of page for chapter or non-chapter identifiers, cleans
                line and increments line counter
                """

                if is_not_chapter(line, metadata):
                        return text_lines, ""
                elif is_chapter(line):
                        line = CHAPTER_MARKER
                text_lines += 1
                return text_lines, desmarten_text(line)

        page_list = []
        paragraph_list = []
        lines = page.split("\n")
        text_lines = 0

        for line in lines:
                if line.strip():
                        if text_lines < 3:
                                text_lines, plain_text = check_beginning_of_page(line, metadata)
                                if plain_text == "":
                                        return plain_text
                        paragraph_list.append(plain_text)
                elif paragraph_list:
                        if not is_end_of_paragraph:
                                continue
                        page_list.append(concatenate_paragraph(paragraph_list))
                        paragraph_list = []

        if paragraph_list:
                page_list.append(concatenate_paragraph(paragraph_list))
        return "\n".join(page_list)

def read_pdf(file_path: str, metadata: dict) -> str:
        """
        Reads the contents of a PDF file and returns it as a string.

        Args:
                file_path: The path to the PDF file.
                metadata: A dictionary containing the title and author of the file.

        Returns:
                A string representing the processed contents of the PDF file.
        """

        def append_page_text(page_text: str, full_text: str) -> str:
                "Append the processed page text to the full text."

                if page_text.rstrip().endswith(END_PARAGRAPH):
                        return full_text + page_text + "\n"
                else:
                        return full_text + page_text + " "

        def process_page_elements(page) -> Tuple[str, str]:
                "Processes the elements of a PDF page."

                pdf_text = ""
                obj_nums = []
                for element in page:
                        obj_type, content = process_element(element)
                        if obj_type == "image":
                                obj_nums.append(content)
                        elif obj_type == "text" and content != "No text found":
                                pdf_text += content + "\n"
                ocr_text = parse_img_obj(file_path, obj_nums)
                return ocr_text, pdf_text

        full_text = ""
        for page in extract_pages(file_path):
                ocr_text, pdf_text = process_page_elements(page)
                page_text = ocr_text + "\n\n" + pdf_text if ocr_text is not None else pdf_text
                pdf_page = parse_pdf_page(page_text, metadata)
                full_text = append_page_text(pdf_page, full_text)

        if full_text.startswith(CHAPTER_MARKER):
                return full_text.lstrip(CHAPTER_MARKER)
        else:
                return full_text
