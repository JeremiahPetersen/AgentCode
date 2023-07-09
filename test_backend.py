import requests
import json

url = 'http://localhost:5000/chat'
headers = {'Content-Type': 'application/json'}
data = {'prompt': 'what does this do - "def load_text_nearest_neighbors(self):"'}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.json())
