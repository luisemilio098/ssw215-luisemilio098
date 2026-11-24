import os
import base64
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"Bearer {token}"} if token else {}

try:
	request = Request(
		"https://api.github.com/repos/pallets/flask/readme",
		headers=headers,
	)
	with urlopen(request, timeout=8) as response:
		status = response.status
		response_headers = response.headers
		body = json.loads(response.read().decode("utf-8"))
except HTTPError as error:
	status = error.code
	response_headers = error.headers
	body = None

print("status:", status)
print("requests left this hour:", response_headers.get("X-RateLimit-Remaining"))
if status == 200:
	readme = base64.b64decode(body["content"]).decode("utf-8")
	print(readme[:80])
else:
	print("GitHub refused. Check GITHUB_TOKEN in .env.")