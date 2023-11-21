import json

import requests

url = "https://factcheck.essentiasoftserv.com/api/chatbot/"
message = "Is the claim about sunil gavaskar criticizing BCCI over handling cricket world cup true?"
data = {"content": message}

headers = {"Content-type": "application/json"}

with requests.post(url, data=json.dumps(data), headers=headers, stream=True) as r:
    for chunk in r.iter_content(1024):
        print(chunk)
