import os
import requests
from dotenv import load_dotenv

load_dotenv()

def call_ai(messages):
  api_key = os.getenv('llama_ai')
  url = "https://api.llama.com/v1/chat/completions"
  headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}", 
  }
  if isinstance(messages, list):
    data = {
    "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
    "messages": messages
  }
  else:
    data = {
      "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": [
          {"role": "user", "content": messages}
        ]
    }
 
  response = requests.post(url, headers=headers, json=data)
  resp_json = response.json()
  content = resp_json["completion_message"]["content"]["text"]
  return content