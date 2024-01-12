import json
import os
import re
import shutil
import uuid
import threading
import time
from collections import deque
from typing import List, Tuple

from openai import OpenAI
import tiktoken
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
training_status = {}
client = OpenAI()
UPLOAD_FOLDER = os.path.join("prosepal", "upload_folder")
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
TOKENIZER = tiktoken.get_encoding("cl100k_base")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def is_utf8(file_path: str) -> bool:
  try:
    with open(file_path, 'r', encoding='utf-8') as file:
      file.read()
    return True
  except UnicodeDecodeError:
    return False

def clear_screen():
  "Clears the the screen using OS-specific commands"

  if os.name == 'nt':
    os.system('cls')
  else:
    os.system('clear')

def processing_psuedo_animation(folder_name: str, message: str):
  for i in range(1,4):
    clear_screen()
    training_status[folder_name] = f"{message}{'.' * i}"
    time.sleep(1)

def read_text_file(file_path: str) -> str:
  with open(file_path, "r") as f:
    read_file = f.read()
  return read_file

def write_jsonl_file(content: str, file_path: str):
  with open(file_path, "a") as f:
    for item in content:
      json.dump(item, f)
      f.write("\n")
  return

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

def generate_beats(book: str, role: str) -> list:
  pass


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

def count_tokens(text: str) -> Tuple[List[int], int]:
  tokens = TOKENIZER.encode(text)
  num_tokens = len(tokens)
  return tokens, num_tokens

def adjust_to_newline(tokens: List[int], end_index: int) -> int:

  newline = 198 # token id for a newline character
  while end_index > 0 and tokens[end_index - 1] != newline:
    end_index -= 1
  return end_index

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

def fine_tune(folder_name: str):

  fine_tune_file = os.path.join(folder_name, "fine_tune.jsonl")

  JSONL_file = client.files.create(
    file = open(fine_tune_file, "rb"),
    purpose = "processing"
  )

  training_status[folder_name] = f"Uploaded file id {JSONL_file.id}"
  message = "processing"
  while True:
    upload_file = client.fine_tuning.jobs.retrieve(id=JSONL_file.id)
    processing_psuedo_animation(folder_name, message)
    if upload_file.status == "processed":
      clear_screen()
      training_status[folder_name] = "File processed"
      break

  fine_tune_job = client.fine_tuning.jobs.create(training_file=JSONL_file.id, model="gpt-3.5-turbo-1105")
  message = "Fine-tuning"
  while True:
    fine_tune_info = client.fine_tuning.jobs.retrieve(id=fine_tune_job.id)
    processing_psuedo_animation(message)
    if fine_tune_info.status == "succeeded":
      training_status[folder_name] = fine_tune_info.status
      training_status[folder_name] = f"Fine-tuned model info {fine_tune_info}"
      training_status[folder_name] = f"Model id {fine_tune_info.fine_tuned_model}"
      break
  return

def process_files(folder_name: str, role: str, chunk_type: str):
  
  fine_tune_messages = []
  for file_name in os.listdir(folder_name):
    if file_name.endswith("txt"):
      for root, _, files in os.walk(folder_name):
        for file in files:
          file_path = os.path.join(root, file)
          content = read_text_file(file_path)
          formatted_messages = split_into_chunks(content, role, chunk_type)
          fine_tune_messages.extend(formatted_messages)
          training_status[folder_name] = f"{file} processed"
  fine_tune_path = os.path.join(folder_name, "fine_tune.jsonl")
  write_jsonl_file(fine_tune_messages, fine_tune_path)
  training_status[folder_name] = "All files processed"
  return

def train(folder_name:str, role: str, user_key: str, chunk_type: str):
  client.api_key = user_key
  process_files(folder_name, role, chunk_type)
  fine_tune(folder_name)

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    author = request.form["author"]
    chunk_type = request.form["chunk_type"]
    user_key = request.form['user_key']

    # Validate user key
    if not (user_key.startswith("sk-") and 50 < len(user_key) > 60):
      return "Invalid user key", 400

    random_folder = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()))
    os.makedirs(random_folder, exist_ok=True)

    for file in request.files.getlist("file"):
      if file and file.filename.endswith(("txt", "text")):
        random_filename = f"{str(uuid.uuid4())}.txt"
        file_path = os.path.join(random_folder, random_filename)
        file.save(file_path)

        if not is_utf8(file_path):
          os.remove(file_path)
          return "File is not UTF-8 encoded", 400
                    
    threading.Thread(target=train, args=(random_folder, user_key, author, chunk_type)).start()
    shutil.rmtree(random_folder)
    del user_key
    del training_status[random_folder]
    return render_template("index.html", folder_name=random_folder.split('/')[-1])

  return render_template("index.html")

@app.route("/status/<folder_name>")
def status(folder_name: str):
    full_path = os.path.join(UPLOAD_FOLDER, folder_name)
    return jsonify({'status': training_status.get(full_path, 'Not started')})

if __name__ == '__main__':
    app.run(debug=True)
