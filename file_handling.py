import json
import os

import chardet

def is_encoding(file_path: str, encoding: str) -> bool:
  try:
    with open(file_path, "r", encoding=encoding) as f:
      f.read()
    return True
  except UnicodeDecodeError:
    return False

def auto_detect_encoding(file_path: str) -> str:
  with open(file_path, 'rb') as f:
    raw_data = f.read()
  return chardet.detect(raw_data)['encoding']

def manual_detect_encoding(file_path: str) -> str:
  for encoding in ["iso-8859-1", "windows-1252", "utf-16", "utf-32", "iso-8859-2", "iso-8859-5", "iso-8859-6", "iso-8859-7", "iso-8859-9"]:
    if is_encoding(file_path, encoding):
      return encoding
  return ""

def recode_text(original_file_path: str) -> str:
  base_name, ext = os.path.splitext(original_file_path)
  recoded_file_path = f"{base_name}-recoded{ext}"
  detected_encoding = auto_detect_encoding(original_file_path) or manual_detect_encoding(original_file_path)
  with open(original_file_path, "r", encoding=detected_encoding or "utf-8", errors="ignore") as f:
    content = f.read()
  with open(recoded_file_path, "w", encoding="utf-8") as f:
    f.write(content)



  
def read_text_file(file_path: str) -> str:
  with open(file_path, "r") as f:
    read_file = f.read()
  return read_file

def write_to_file(content: str, file: str):
  with open(file, "w") as f:
    f.write(content)

def write_jsonl_file(content: str, file_path: str):
  with open(file_path, "a") as f:
    for item in content:
      json.dump(item, f)
      f.write("\n")
  return