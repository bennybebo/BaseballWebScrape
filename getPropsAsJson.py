import http.client
import os
import json
from datetime import datetime

conn = http.client.HTTPSConnection("api.actionnetwork.com")

payload = ""
headers = { 'authority': "api.actionnetwork.com" }

# Calculate the current date in the desired format
current_date = datetime.now().strftime("%Y%m%d")

conn.request("GET", "/web/v1/leagues/8/props/core_bet_type_33_hr?bookIds=69%2C75%2C68%2C123%2C71%2C32%2C76%2C79&date=" + current_date, payload, headers)

res = conn.getresponse()
data = res.read()
json_data = data.decode("utf-8")
parsed_json = json.loads(json_data)
# Get the current working directory
current_directory = os.getcwd()
# Construct the file path for the JSON file in the same directory
file_path = os.path.join(current_directory, "data.json")
# Save the JSON data to the file
with open(file_path, "w") as file:
    json.dump(parsed_json, file)
print("JSON file saved successfully!")