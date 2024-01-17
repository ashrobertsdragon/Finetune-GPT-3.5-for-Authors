import json

def is_utf8(file_path: str) -> bool:
  try:
    with open(file_path, "r", encoding="utf-8") as file:
      file.read()
    return True
  except UnicodeDecodeError:
    return False
  
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