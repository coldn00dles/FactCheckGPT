import json

import requests

url = "http://127.0.0.1:5000/api/chatbot/"
message = "Is there any information about obama meeting sadhguru in washington?"
data = {"content": message}

headers = {"Content-type": "application/json"}

with requests.post(url, data=json.dumps(data), headers=headers, stream=True) as r:
    for chunk in r.iter_content(None, decode_unicode=True):
        if chunk:
            print(chunk, end='', flush=True)