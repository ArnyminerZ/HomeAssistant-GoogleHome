#!/usr/bin/python

import os
import sys, getopt
import json
import requests
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from get_tokens import master_token, access_token
from load_params import device_ip, device_name, fetch_path

if master_token is None:
    print("Master token not found")
    sys.exit(1)
if access_token is None:
    print("Access token not found")
    sys.exit(1)

if device_name is None or device_ip is None or fetch_path is None:
    print("ghome_get.py -i <device-ip> -n <device-name> -p <path> -o [output]")
    sys.exit(1)

script_path = Path(os.path.realpath(__file__))
script_dir_path = script_path.parent

lat_result = os.popen(f"{script_dir_path}/grpcurl -H 'authorization: Bearer {access_token}' -import-path {script_dir_path} -proto {script_dir_path}/google/internal/home/foyer/v1.proto googlehomefoyer-pa.googleapis.com:443 google.internal.home.foyer.v1.StructuresService/GetHomeGraph | jq '.home.devices[] | {{deviceName, localAuthToken}}'")
lat_data = lat_result.read()[:-1] # -1 for removing the last line jump
lat_data = "[" + lat_data.replace("}", "},")[:-1] + "]" # Format the JSON correctly

found_device = False
for element in json.loads(lat_data):
    token = element["localAuthToken"]
    name = element["deviceName"]
    if token is None:
        continue
    if name == device_name:
        found_device = True
        get_request = requests.get(
            f"https://{device_ip}:8443/setup{fetch_path}",
            headers={'cast-local-authorization-token': token},
            verify=False,
        )
        request_json = get_request.text
        print(request_json)

if not found_device:
    print("Error: The specified device was not found. Check your parameters.")