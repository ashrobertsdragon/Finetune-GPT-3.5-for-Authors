import base64
import logging
import os

import openai
from openai import OpenAI

error_logger = logging.getLogger("error_logger")


def encode_image(image_path):
    "Encode an image to base64"
    
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_api(payload: dict) -> str:
    "Call OpenAI's ChatCompletions API endopoint for OCR or double-checking response"

    api_key = os.getenv("PROSEPAL_OCR_KEY")
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(payload)
        if response.json()["choices"]:
            answer = response.json()["choices"][0]["message"]["content"]
            return answer
        if response.json()["error"]:
            error = response.json()["error"]["message"]
            raise Exception(error)
    except KeyError as e:
        error_logger.exception(f"Error: {e}\nResponse: {response.text}")
        return ""
    except openai.APIStatusError as e:
        if e.status_code==429:
            client.close()
            client = OpenAI(api_key=os.environ("PROSEPAL_OCR_KEY_FALLBACK"))
            return call_api(payload)
    except Exception as e:
        error_logger.exception(f"Error: {e}")
        return ""

def double_check_answer(ocr_text: str) -> str:
    "Use GPT 3.5 to translate garbled OCR response"

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": (
                "You are double checking the output of an OCR application, which may be "
                "garbled. Based on the text below, please respond with what the text should "
                "actually be, without any additional commentary."
            )},
            {"role": "user", "content": ocr_text},
        ],
        "max_tokens": 10
    }
    return call_api(payload)

def run_ocr(base64_images: list) -> str:
    """
    Create payload for OpenAI API call to GPT-4 Vision for OCR, based on list of
    base64 encoded images. Call API for OCR and then again with GPT-3.5 to double
    check response.

    Arguments:
        base64_images (list): A list of base64-encoded images.

    Returns str: The recognized text from the images.
    """

    image_role_list = []

    for base64_image in base64_images:
        image_role_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "low"
            }
        })
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [{
            "role": "user",
            "content": [{
                "type": "text",
                "text": (
                    "Please provide the text in these images as a single combined "
                    "statement with spaces as appropriate without any commentary. Use "
                    "your judgment on whether consecutive images are a single word or "
                    "multiple words. If there is no text in the image, or it is "
                    "unreadable, respond with 'No text found'"
                )},
                *image_role_list
            ]
        }],
        "max_tokens": 10
    }
    ocr_text = call_api(payload)
    if ocr_text:
        return double_check_answer(ocr_text)
    else:
        return ""