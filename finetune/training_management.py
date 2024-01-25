import os
import shutil
import time

from file_handling import read_text_file, write_jsonl_file
from finetune.chunking import split_into_chunks
from finetune.openai_client import client, set_client
from finetune.shared_resources import initialize_dictionary, training_status


def psuedo_animation(folder_name: str, message: str):
  """Simulate a animation by updating the training status with a message and
    a cyclically changing number dots."""

  for i in range(1,4):
    training_status[folder_name] = f"{message}{'.' * i}"
    time.sleep(1)

def fine_tune(folder_name: str):
  """
  Fine-tunes a language model using the specified data.

  This function uploads the JSONL fine-tuning data file, monitors its processing,
  and initiates fine-tuning on the specified model. It updates the training status
  as the fine-tuning process progresses.

  Args:
    folder_name (str): The name of the folder containing the fine-tuning data file.

  Returns:
    None
  """

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

def process_files(folder_name: str, role: str, chunk_type: str) -> str:
  """
  Process book files into formatted messages for fine-tuning.

  This function iterates through the text files in the specified folder, reads
  their content, splits them into chunks based on the specified system role and
  chunk type, and collects the formatted messages for fine-tuning. It updates
  the training status as files are processed.

  Args:
    folder_name (str): The name of the folder containing book files.
    role (str): The system message to be used in fine-tuning.
    chunk_type (str): The type of chunking to be applied.

  Returns:
    str: The path to the generated JSONL file containing fine-tuning messages.
  """

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
  return fine_tune_path

def train(folder_name: str, role: str, user_key: str, chunk_type: str):
  """
  Sets up the process for processing book files into training data and finetuning
  a LLM. This function sets up the necessary OpenAI client using the user's API key,
  initializes a the training_status dictionary if it hasn't been intialized, processes
  files in the specified folder, and performs fine-tuning.
  After training is complete, a download link to the JSONL file is provided.

  Note: This function deletes the user_key after use for security reasons.

  Args:
    folder_name (str): The name of the folder containing the user's books.
    role (str): The system message to be used in fine tuning.
    user_key (str): The user's API key.
    chunk_type (str): The type chunking to be used.

  Returns:
    None
  """

  set_client(user_key)
  initialize_dictionary()
  fine_tune_path = process_files(folder_name, role, chunk_type)
  fine_tune(folder_name)
  download_path = os.path.relpath(fine_tune_path, start=os.path.join("app", "upload_folder"))
  training_status[folder_name] = f"Download <a href='/download/{download_path}'>JSONL file here</a>."
  del user_key