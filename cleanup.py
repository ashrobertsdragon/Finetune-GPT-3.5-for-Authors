import logging
import os
import shutil
import time

from finetune.shared_resources import training_status

error_logger = logging.getLogger('error_logger')

def cleanup_directory(UPLOAD_FOLDER):
  while True:
    now = time.time()
    for folder_name in os.listdir(UPLOAD_FOLDER):
      folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
      if os.path.isdir(folder_path):
        try:
          shutil.rmtree(folder_path)
          del training_status[folder_name]
        except Exception as e:
          creation_time = os.path.getctime(folder_path)
          time_passed = now - creation_time
          if time_passed > 3600:
            length_time = f"{time_passed//60} minutes {round(time_passed%60)}seconds"
            error_logger.exception(f"{folder_path} still locked after {length_time}.\n{e}")
    time.sleep(3600)  # Wait for 1 hour before next cleanup