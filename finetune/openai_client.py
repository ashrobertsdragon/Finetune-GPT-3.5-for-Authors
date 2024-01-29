from openai import OpenAI

client = None

def set_client(api_key:str):
  global client
  api_key = api_key
  client = OpenAI()

def get_client():
  return client
