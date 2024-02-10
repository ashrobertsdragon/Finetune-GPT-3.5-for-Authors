from openai import OpenAI

client = None

def set_client(api_key:str):
  global client
  client = OpenAI(api_key = api_key)

def get_client():
  return client
