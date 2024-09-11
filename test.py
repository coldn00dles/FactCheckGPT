import json

import requests

url = "http://127.0.0.1:5050/api/chatbot/"
message = str(input("What would you like to ask today?"))
data = {"content": message}

headers = {"Content-type": "application/json"}

with requests.post(url, data=json.dumps(data), headers=headers, stream=True) as r:
    for chunk in r.iter_content(None, decode_unicode=True):
        if chunk:
            print(chunk, end='', flush=True)