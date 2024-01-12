import json
import os
import re
import shutil
import uuid
import threading
import time
from collections import deque

from openai import OpenAI
import tiktoken
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
training_status = {}
client = OpenAI()
UPLOAD_FOLDER = '/path/to/non-web-accessible-folder'
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def is_utf8(file_path):
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

def processing_psuedo_animation(folder_name, message):
  for i in range(1,4):
    clear_screen()
    training_status[folder_name] = f"{message}{'.' * i}"
    time.sleep(1)

def read_text_file(file_path):
  with open(file_path, "r") as f:
    read_file = f.read()
  return read_file

def write_jsonl_file(content, file_path):
  with open(file_path, "a") as f:
    for item in content:
      json.dump(item, f)
      f.write("\n")
  return

def separate_into_chapters(text):
  return re.split(r"\s*\*\*\s*", text)

def split_into_chunks(chapter, chunk_size = 2000):

  tokenizer = tiktoken.get_encoding("cl100k_base")
  tokens = tokenizer.encode(chapter)
  chunks = []

  for i in range(0, len(tokens), chunk_size):
    chunk_tokens = tokens[i:i + chunk_size]
    chunks.append(tokenizer.decode(chunk_tokens))
  return chunks

def format_for_fine_tuning(chunks, author):
  
  system_message = f"You are a junior author who writes in the style of {author}"
  formatted_data = []
  queue = deque(chunks)

  while len(queue) > 1:
    user_message = queue.popleft()
    assistant_message = queue[0]
    message = {
      "messages": [
        { "role": "system", "content": system_message },
        { "role": "user", "content": user_message },
        { "role": "assistant", "content": assistant_message }
      ]
    }
    formatted_data.append(message)
  return formatted_data

def fine_tune(folder_name, api_key):
  
  client.api_key = api_key

  fine_tune_file = os.path.join(folder_name, "fine_tune.jsonl")

  JSONL_file = client.files.create(
    file = open(fine_tune_file, "rb"),
    purpose = "processing"
  )

  training_status[folder_name] = f"Uploaded file id {JSONL_file.id}"
  message = "processing"
  while True:
    upload_file = client.files.retrieve(id=JSONL_file.id)
    processing_psuedo_animation(folder_name, message)
    if upload_file.status == "processed":
      clear_screen()
      training_status[folder_name] = "File processed"
      break

  fine_tune_job = client.fine_tuning.jobs.create(training_file=JSONL_file.id, model="gpt-3.5-turbo-1105")
  message = "Fine-tuning"
  while True:
    fine_tune_info = client.fine_tuning.job.retrieve(id=fine_tune_job.id)
    processing_psuedo_animation(message)
    if fine_tune_info.status == "succeeded":
      training_status[folder_name] = fine_tune_info.status
      training_status[folder_name] = f"Fine-tuned model info {fine_tune_info}"
      training_status[folder_name] = f"Model id {fine_tune_info.fine_tuned_model}"
      break
  return

def process_files(folder_name, author):
  
  fine_tune_messages = []
  for file_name in os.listdir(folder_name):
    if file_name.endswith("txt"):
      for root, _, files in os.walk(folder_name):
        for file in files:
          file_path = os.path.join(root, file)
          content = read_text_file(file_path)
          chapters = separate_into_chapters(content)

          for chapter in chapters:
            chunks = split_into_chunks(chapter)
            formatted_messages = format_for_fine_tuning(chunks, author)
            fine_tune_messages.extend(formatted_messages)

          training_status[folder_name] = f"{file} processed"
  fine_tune_path = os.path.join(folder_name, "fine_tune.jsonl")
  write_jsonl_file(fine_tune_messages, fine_tune_path)
  training_status[folder_name] = "All files processed"
  return

def train(folder_name, author, user_key):
  process_files(folder_name, author)
  fine_tune(folder_name, user_key)

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
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
                    
    threading.Thread(target=train, args=(random_folder, user_key)).start()
    shutil.rmtree(random_folder)
    del user_key
    del training_status[random_folder]
    return render_template("index.html", folder_name=random_folder.split('/')[-1])

  return render_template("index.html")

@app.route("/status/<folder_name>")
def status(folder_name):
    full_path = os.path.join(UPLOAD_FOLDER, folder_name)
    return jsonify({'status': training_status.get(full_path, 'Not started')})

if __name__ == '__main__':
    app.run(debug=True)
