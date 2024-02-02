import time
import logging
from typing import Any, Optional

import openai

from finetune.openai_client import get_client
from finetune.shared_resources import training_status, thread_local_storage

error_logger = logging.getLogger("error_logger")


def check_json_response(response: Any) -> dict:
  """Attempt to parse JSON safely. Return None if parsing fails."""

  try:
    return response.json()
  except ValueError:
    return {} 

def error_handle(e: Any, retry_count: int = 0) -> int:
  """
  Determines whether error is unresolvable or should be retried. If unresolvable,
  error is logged and administrator is emailed before exit. Otherwise, exponential
  backoff is used for up to 5 retries.

  Args:
    e: an Exception body
    retry_count: the number of attempts so far

  Returns:
    retry_count: the number of attemps so far
  """

  unresolvable_user_errors = [
    openai.BadRequestError,
    openai.AuthenticationError,
    openai.NotFoundError,
    openai.PermissionDeniedError
  ]
  error_image = '<img src="/static/alert-light.png" alt="error icon" id="endError">'
  user_folder = getattr(thread_local_storage, "user_folder", None)
  error_code = getattr(e, "status_code", None)
  error_details = {}
  if hasattr(e, "response"):
    json_data = check_json_response(e.response)
    if json_data is not {}:
      error_details = json_data.get("error", {})
  error_message = error_details.get("message", "Unknown error")
  error_logger.error(f"{e}. Error code: {error_code}. Error message: {error_message}")

  if isinstance(e, tuple(unresolvable_user_errors)) or error_code == 401 or "exceeded your current quota" in error_message:
    if user_folder:
      training_status[user_folder] = f"{error_image} {error_message}"

  if(isinstance(e, openai.UnprocessableEntityError)):
    if user_folder:
      training_status[user_folder] = f"{error_image} A critical error has occured. The administrator has been contacted. Sorry for the inconvience"

  retry_count += 1
  if retry_count > 5:
    error_logger("Retry count exceeded")
    if user_folder:
      training_status[user_folder] = "A critical error has occured. The administrator has been contacted. Sorry for the inconvience"
  else:
    sleep_time = (5 - retry_count)  + (retry_count ** 2)
    time.sleep(sleep_time)
  return retry_count

def call_gpt_api(prompt: str, retry_count: Optional[int] = 0) -> str:
  """
  Makes API calls to the OpenAI ChatCompletions engine.

  Args:.
    prompt (str): The user's prompt.
    retry_count (int, optional): The number of retry attempts. Defaults to 0.

  Returns:
    str: The generated content from the OpenAI GPT-3 model.
  """
  
  client = get_client()

  role_script = (
    "You are an expert develompental editor who specializes in writing scene beats "
    "that are clear and concise. For the following chapter, please reverse engineer "
    "the scene beats for the author. Provide only the beats and not any commentary "
    "the beginning or end."
  )
  messages = [
      {"role": "system", "content": role_script},
      {"role": "user", "content": prompt}
  ]

  try:
    response = client.chat.completions.create(
      model = "gpt-3.5-turbo-1106",
      messages = messages,
      temperature = 0.7,
      max_tokens = 1000,
    )
    if response.choices and response.choices[0].message.content:
      answer = response.choices[0].message.content.strip()
    else:
      raise Exception("No message content found")

  except Exception as e:
    retry_count = error_handle(e, retry_count)
    answer = call_gpt_api(prompt, retry_count)
  return answer
