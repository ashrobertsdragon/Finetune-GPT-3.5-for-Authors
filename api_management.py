import time
from typing import Any, Optional

import openai

from app import client


def error_handle(e: Any, retry_count: int) -> int:
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

  unresolvable_errors = [
    openai.BadRequestError,
    openai.AuthenticationError,
    openai.NotFoundError,
    openai.PermissionDeniedError,
    openai.UnprocessableEntityError
  ]

  error_code = getattr(e, "status_code", None)
  error_details = getattr(e, "response", {}).json().get("error", {})
  error_message = error_details.get("message", "Unknown error")

  if isinstance(e, tuple(unresolvable_errors)):
    exit(1)
  if error_code == 401:
    exit(1)
  if "exceeded your current quota" in error_message:
    exit(1)

  retry_count += 1
  if retry_count == 5:
    exit(1)
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
