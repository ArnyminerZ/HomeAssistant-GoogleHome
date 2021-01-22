import os
import sys, getopt
import json
import requests
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from get_tokens import master_token, access_token
from load_params import device_ip, device_name

if master_token is None:
    print("Master token not found")
    sys.exit(1)
if access_token is None:
    print("Access token not found")
    sys.exit(1)

if device_name is None or device_ip is None:
    print("get_alarms.py -i <device-ip> -n <device-name>")
    sys.exit(1)

script_path = Path(os.path.realpath(__file__))
script_dir_path = script_path.parent

lat_result = os.popen(f"{script_dir_path}/grpcurl -H 'authorization: Bearer {access_token}' -import-path {script_dir_path} -proto {script_dir_path}/google/internal/home/foyer/v1.proto googlehomefoyer-pa.googleapis.com:443 google.internal.home.foyer.v1.StructuresService/GetHomeGraph | jq '.home.devices[] | {{deviceName, localAuthToken}}'")
lat_data = lat_result.read()[:-1] # -1 for removing the last line jump
lat_data = "[" + lat_data.replace("}", "},")[:-1] + "]" # Format the JSON correctly
lat_items = []

# Now, remove the items that doesn't provide a valid local auth token
for element in json.loads(lat_data):
    if element["localAuthToken"] is not None:
        lat_items.append(element)

print(lat_items)