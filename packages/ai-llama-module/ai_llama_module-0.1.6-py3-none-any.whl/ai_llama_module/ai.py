import os
import requests
from dotenv import load_dotenv

load_dotenv()

def call_ai(messages, model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8", api_key: str = os.getenv('llama_ai')):
  api_key = api_key
  if not api_key:
    print("No API key found, it should be called 'llama_ai' as the key name.")
  url = "https://api.llama.com/v1/chat/completions"
  headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}", 
  }
  if isinstance(messages, list):
    data = {
    "model": model,
    "messages": messages
  }
  else:
    data = {
      "model": model,
        "messages": [
          {"role": "user", "content": messages}
        ]
    }
  
  response = requests.post(url, headers=headers, json=data)
  resp_json = response.json()
  try:
      content = resp_json["completion_message"]["content"]["text"]
  except KeyError:
      raise ValueError(f"Unexpected response format: {resp_json}")
  return content