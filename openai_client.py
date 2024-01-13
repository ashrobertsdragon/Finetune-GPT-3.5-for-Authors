from openai import OpenAI


client = None

def set_client(api_key:str):
  global client
  client = OpenAI()
