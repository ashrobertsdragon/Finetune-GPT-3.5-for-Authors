import os
import shutil
import time

from file_handling import read_text_file, write_jsonl_file
from finetune.chunking import split_into_chunks
from finetune.openai_client import client, set_client
from finetune.shared_resources import initialize_dictionary, training_status


def psuedo_animation(folder_name: str, message: str):
  for i in range(1,4):
    training_status[folder_name] = f"{message}{'.' * i}"
    time.sleep(1)

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
    psuedo_animation(folder_name, message)
    if upload_file.status == "processed":
      training_status[folder_name] = "File processed"
      break

  fine_tune_job = client.fine_tuning.jobs.create(training_file=JSONL_file.id, model="gpt-3.5-turbo-1105")
  message = "Fine-tuning"
  while True:
    fine_tune_info = client.fine_tuning.jobs.retrieve(id=fine_tune_job.id)
    psuedo_animation(message)
    if fine_tune_info.status == "succeeded":
      training_status[folder_name] = (
        f"{fine_tune_info.status}"
        f"Fine-tuned model info {fine_tune_info}"
        f"Model id {fine_tune_info.fine_tuned_model}"
      )
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
  set_client(user_key)
  initialize_dictionary()
  process_files(folder_name, role, chunk_type)
  fine_tune(folder_name)
  shutil.rmtree(folder_name)
  del user_key
  del training_status[folder_name]
