from typing import Tuple

from api_management import call_gpt_api
from data_preparation import adjust_to_newline, count_tokens, format_for_finetuning, separate_into_chapters, sliding_window_format, TOKENIZER


def generate_beats(book: str, role: str) -> list:

  user_message = []
  chunks = []
  chapters = separate_into_chapters(book)

  for chapter in chapters:
    words = len(chapter.split(" "))
    prompt = f"Chapter: {chapter}"
    chapter_beats = call_gpt_api(prompt)
    user_message.append(
      f"Write {words} words for a chapter with the following scene beats:\n{chapter_beats}"
    )
    chunks.append(chapter)
    return format_for_finetuning(chunks, role, user_message)

def extract_dialogue(paragraph: str) -> Tuple[str, str]:

  dialogue = ""
  prose = ""
  sentence = ""
  check_next_char = False
  end_sentence = False
  in_dialogue = False
  punctuation = [".", "?", "!"]
  quote_count = 0

  for i, char in enumerate(paragraph):
    sentence += char
    if char == '"':
      quote_count += 1
      in_dialogue = True if (quote_count // 2 == 1) else False
      end_sentence = True if check_next_char is True else False
      check_next_char = False
    if char in punctuation:
      if i + 1 < len(paragraph):
        check_next_char = True
        continue
      end_sentence = True
    if end_sentence is True:
      if in_dialogue is False:
        prose += sentence.strip()
      elif in_dialogue is True:
        dialogue += sentence.strip()
      sentence = ""
      end_sentence = False
  return prose, dialogue

def dialogue_prose(book: str, role: str) -> list:

  chunks = []
  user_message = []
  punctuation = [".", "?", "!"]
  prose_sentences = 0
  dialogue_sentences = 0
  chapters = separate_into_chapters(book)

  for chapter in chapters:
    paragraphs = chapter.split("\n")
    for paragraph in paragraphs:
      prose, dialogue = extract_dialogue(paragraph)
      for mark in punctuation:
        prose_sentences += prose.count(mark)
        dialogue_sentences += dialogue.count(mark)
      if prose:
        chunks.append(prose)
        user_message.append(f"Write {prose_sentences} sentences of description action")
      if dialogue:
        chunks.append(dialogue)
        user_message.append(f"Write {dialogue_sentences} sentences of dialogue")
  return format_for_finetuning(chunks, role, user_message)

def sliding_window_large(book: str) -> list:

  chunk_list = []
  chunk_size = 4096
  start_index = 0
  tokens, num_tokens = count_tokens(book)

  while start_index < num_tokens:
    end_index = min(start_index + chunk_size, num_tokens)
    # Adjust end_index to the last newline token in the chunk
    if end_index < num_tokens:
      end_index = adjust_to_newline(tokens, end_index)
    chunk_tokens = tokens[start_index:end_index]
    chunk_list.append(TOKENIZER.decode(chunk_tokens))
    start_index = end_index
  return chunk_list

def sliding_window_small(book: str) -> list:

  chunk_list = []
  chapters = separate_into_chapters(book)

  for chapter in chapters:
    tokens, chapter_token_count = count_tokens(chapter)
    chunk_size = min(chapter_token_count / 3, 4096)
    start_index = 0

    while start_index < chapter_token_count:
      end_index = min(start_index + chunk_size, chapter_token_count)
      # Adjust end_index to the last newline token in the chunk
      if end_index < chapter_token_count:
        end_index = adjust_to_newline(tokens, end_index)
      chunk_tokens = tokens[start_index:end_index]
      chunk_list.append(TOKENIZER.decode(chunk_tokens))
      start_index = end_index
  return chunk_list

def split_into_chunks(content: str, role: str, chunk_type: str) -> list:
    
  if chunk_type == "sliding_window_small":
    chunks = sliding_window_small(content)
    formatted_messages = sliding_window_format(chunks, role, chunk_type)
  if chunk_type == "sliding_window_large":
    formatted_messages = sliding_window_format(chunks, role, chunk_type)
  if chunk_type == "dialogue_pass":
    formatted_messages = dialogue_prose(chunks, role, chunk_type)
  if chunk_type == "generate_beats":
    formatted_messages = generate_beats(chunks, role, chunk_type)
  return formatted_messages