import requests
import json

url = "http://localhost:5000/api/jira/projects/"
response = requests.get(url)
print(response.text)

# url = "http://localhost:5000/api/files/admin"
# response = requests.get(url)
# print(response.text)


# url = "http://localhost:5000/api/ask/tm/testscripts"
# headers = {"Content-Type": "application/json"}
# data = {"question" : "As a network engineer, how to enable the beacon mode for an Ethernet port to flash its LED to confirm its physical location for cisco configuration guide cli commands","language":"python","tc_id":"74125"}
# response = requests.post(url, headers=headers, data=json.dumps(data))
# print(response.text)