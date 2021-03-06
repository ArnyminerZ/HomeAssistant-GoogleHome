#!/usr/bin/python

import os, sys, random
import requests
from pathlib import Path
import time
from glocaltokens.client import GLocalAuthenticationTokens

from dotenv import load_dotenv
load_dotenv()

from paho.mqtt import client as mqtt_client
from load_params import device_ip, device_name, fetch_path, output_param, use_json

import urllib3
if use_json:
    urllib3.disable_warnings()


USERNAME = data.get("username", os.getenv("GOOGLE_USERNAME")) if 'data' in globals() else os.getenv("GOOGLE_USERNAME")
PASSWORD = data.get("password", os.getenv("GOOGLE_PASSWORD")) if 'data' in globals() else os.getenv("GOOGLE_PASSWORD")

client = GLocalAuthenticationTokens(
  username=USERNAME,
  password=PASSWORD
)

# Get master token
master_token = client.get_master_token()
if not use_json:
    print('[*] Master token', master_token)

# Get access token (lives 1 hour)
access_token = client.get_access_token()
if not use_json:
    print('\n[*] Access token (lives 1 hour)', access_token)

# Get google device local authentication tokens (live about 1 day)
google_devices = client.get_google_devices_json()
if not use_json:
    print('\n[*] Google devices local authentication tokens')
    print(google_devices)


if device_name is None or device_ip is None or fetch_path is None:
    if not use_json:
        print("ghome_get.py [-h] [-j] -i <device-ip> -n <device-name> -p <path> -o [output]")
    sys.exit(1)

def connect_mqtt(broker, port, username, password, client_id, topic, contents):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            if not use_json:
                print("Connected to MQTT Broker!")
                print(f"  Publishing to {topic}...", end=None)
            client.publish(topic, contents)
            if not use_json:
                print("ok")
        else:
            if not use_json:
                print(f"Failed to connect, return code {rc}")
            sys.exit(1)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    if username is not None:
        client.username_pw_set(username, password)
    client.connect(broker, port)
    return client

script_path = Path(os.path.realpath(__file__))
script_dir_path = script_path.parent

found_device = False
for element in google_devices:
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
                if not use_json:
                    print("Publishing through MQTT...")
                # Get without mqtt://
                req = output_param[7:]
                # Split from topic
                splt = req.split("/")
                # Get first half
                where = splt[0]
                # Get topic
                topic = ""
                for i in range(1, len(splt)):
                    topic += f"/{splt[i]}"
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

                if username is not None and not use_json:
                    print(f"  Authentication required (username:{username},pass={password}).")

                client_id = "ghome_" + str(random.randint(0, 1000))
                client = connect_mqtt(address, port, username, password, client_id, topic, request_json)
                client.loop_start()
                time.sleep(2)
            elif not use_json:
                print("Found an output parameter, but the contents are not valid.")
                print("Please check README for orientation on how to run the command: https://github.com/ArnyminerZ/HomeAssistant-GoogleHome#running")

if not found_device and not use_json:
    print("Error: The specified device was not found. Check your parameters.")