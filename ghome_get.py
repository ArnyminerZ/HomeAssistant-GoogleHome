#!/usr/bin/python

import os, sys, random
import json
import requests
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from get_tokens import master_token, access_token
from load_params import device_ip, device_name, fetch_path, output_param

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

        # Perform all the outputs
        if output_param is not None:
            if output_param.startswith("mqtt://"):
                print("Publishing through MQTT...")
                # Get without mqtt://
                req = output_param[7:]
                # Split from topic
                splt = req.split("/")
                # Get first half
                where = splt[0]
                # Get topic
                topic = splt[1]
                # Divide auth and host
                splt = where.split("@")
                # Get auth and host
                auth = splt[0]
                host = splt[1]
                # Get username and password
                splt = auth.split(":") if len(auth) > 0 else None
                username = splt[0] if splt is not None else None
                password = splt[1] if splt is not None else None
                # Get address and port
                splt = host.split(":")
                address = splt[0]
                port = int(splt[1])

                # Import MQTT
                import paho.mqtt.client as mqtt

                def on_connect(client, userdata, flags, rc):
                    print("ok! Result code "+str(rc))

                    client.loop_start()
                    client.publish(topic, request_json)
                    client.disconnect()
                    client.loop_stop()

                def on_disconnect(client, userdata, rc):
                    print("Disconnected from MQTT.")

                client = mqtt.Client("ghome_" + str(random.randint(0, 1000)))
                client.on_connect = on_connect
                client.on_disconnect = on_disconnect
                if username is not None:
                    print(f"  Authentication required (username:{username},pass={password}).")
                    client.username_pw_set(username, password)
                print(f"  Connecting to {address}:{port}...", end=None)
                client.connect(address, port) # Keep alive for 30 seconds
            else:
                print("Found an output parameter, but the contents are not valid.")
                print("Please check README for orientation on how to run the command: https://github.com/ArnyminerZ/HomeAssistant-GoogleHome#running")

if not found_device:
    print("Error: The specified device was not found. Check your parameters.")