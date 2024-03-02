import os
import time
from datetime import timedelta

import openai

from file_handling import read_text_file, upload_file_to_gcs, write_jsonl_file, initialize_GCStorage
from send_email import email_admin
from finetune.chunking import split_into_chunks
from finetune.openai_client import get_client, set_client
from finetune.shared_resources import training_status, thread_local_storage


def generate_url(gcs_file: str) -> str:
  """
  Generate's signed url from Google Cloud Storage for user to download JSONL file.

  Args:
    None

  Returns:
    str: The signed url for the JSONL file.
  """
  bucket = initialize_GCStorage()
  blob = bucket.blob(gcs_file)
  return blob.generate_signed_url(expiration=timedelta(hours=2), method='GET')


def psuedo_animation(user_folder: str, message: str):
  """Simulate a animation by updating the training status with a message and
    a cyclically changing number dots."""
  
  original_message = training_status[user_folder]
  for i in range(1, 4):
    training_status[user_folder] = f"{original_message}<p>{message}{'.' * i}</p>"
    time.sleep(5)

def fine_tune(folder_name: str, user_folder: str, retry_count: int=0):
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
  if retry_count:
    time.sleep(retry_count**retry_count)

  client = get_client()
  fine_tune_file = os.path.join(folder_name, "fine_tune.jsonl")

  try:
    JSONL_file = client.files.create(
      file = open(fine_tune_file, "rb"),
      purpose = "fine-tune"
    )
    training_status[user_folder] += "<p>Fine-tuning file uploaded</p>"
    print(training_status[user_folder])
    fine_tune_job = client.fine_tuning.jobs.create(training_file=JSONL_file.id, model="gpt-3.5-turbo-1106")
    while True:
      fine_tune_info = client.fine_tuning.jobs.retrieve(fine_tune_job.id)
      psuedo_animation(user_folder, "Finetuning")
      if fine_tune_info.status == "succeeded":
        training_status[user_folder] += (
          f"<p>{fine_tune_info.status}</p>"
          f"<p>Fine-tuned model info {fine_tune_info}</p>"
          f"<p>Model id {fine_tune_info.id }</p>"
        )
        break
      else:
        current_event = client.fine_tuning.jobs.list_events(
          fine_tuning_job_id=fine_tune_job.id,
          limit = 1
        )
        if "data" in current_event and isinstance(current_event["data"], list) and len(current_event["data"]) > 0 and "message" in current_event["data"][0]:
          training_status[user_folder] += f"<p>{current_event['data'][0]['message']}</p>"
  except openai.NotFoundError as e:
    email_admin(e)
    return
  except (openai.AuthenticationError, openai.BadRequestError, openai.PermissionDeniedError, openai.RateLimitError)as e:
    training_status[user_folder] += f"<p>{e.message}</p>"
    return
  except (openai.APIConnectionError, openai.APITimeoutError, openai.ConflictError, openai.InternalServerError, openai.UnprocessableEntityError) as e:
    retry_count += 1
    if retry_count > 3:
      training_status[user_folder] += "<p>A critical error has occured. The administrator has been contacted. Sorry for the inconvience</p>"
      email_admin(e)
      return
    fine_tune(folder_name, user_folder, retry_count)

def process_files(folder_name: str, role: str, chunk_type: str, user_folder: str) -> str:
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
  txt_files = [file for file in os.listdir(folder_name) if file.endswith("txt")]
  total_files = len(txt_files)

  starting_message = training_status[user_folder]
  for i, file_name in enumerate(os.listdir(folder_name), start=1):
    if file_name.endswith("txt"):
      file_path = os.path.join(folder_name, file_name)
      book = read_text_file(file_path)
      formatted_messages = split_into_chunks(book, role, chunk_type)
      fine_tune_messages.extend(formatted_messages)
      training_status[user_folder] = f"{starting_message}<p>File {i} of {total_files} processed</p>"
  training_status[user_folder] += "<p>All files processed</p>"
  fine_tune_path = os.path.join(folder_name, "fine_tune.jsonl")
  write_jsonl_file(fine_tune_messages, fine_tune_path)
  training_status[user_folder] += "<p>Preparing JSONL file for download</p>"
  gcs_file = f"{user_folder}_fine_tune.jsonl"
  upload_file_to_gcs(fine_tune_path, gcs_file)

  return gcs_file

def train(folder_name: str, role: str, user_key: str, chunk_type: str, user_folder: str):
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

  training_status[user_folder] = "<p>Processing files</p>"
  set_client(user_key)
  del user_key
  thread_local_storage.user_folder = user_folder
  gcs_file = process_files(folder_name, role, chunk_type, user_folder)
  download_path = generate_url(gcs_file)
  training_status[user_folder] += f"<p>Download <a href='{download_path}'>JSONL file here</a>.</p>"
  fine_tune(folder_name, user_folder)
