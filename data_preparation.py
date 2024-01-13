import re
from collections import deque
from typing import List, Tuple

import tiktoken

TOKENIZER = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> Tuple[List[int], int]:
  tokens = TOKENIZER.encode(text)
  num_tokens = len(tokens)
  return tokens, num_tokens

def adjust_to_newline(tokens: List[int], end_index: int) -> int:

  newline = 198 # token id for a newline character
  while end_index > 0 and tokens[end_index - 1] != newline:
    end_index -= 1
  return end_index

def format_for_finetuning(chunks: list, role: str, user_message: str) -> list:

  formatted_data = []
  for i, chunk in enumerate(chunks):
    user_content = user_message[i]
    message = {
      "messages": [
        {"role": "system", "content": role},
        {"role": "user", "content": user_content},
        {"role": "assistant", "content": chunk}
      ]
    }
    formatted_data.append(message)
  return formatted_data

def separate_into_chapters(text: str) -> List:
  return re.split(r"\s*\*\*\s*", text)

def sliding_window_format(chunks: list, role: str) -> list:
  
  formatted_data = []
  queue = deque(chunks)

  while len(queue) > 1:
    user_message = queue.popleft()
    assistant_message = queue[0]
    message = {
      "messages": [
        {"role": "system", "content": role},
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_message}
      ]
    }
    formatted_data.append(message)
  return formatted_data
