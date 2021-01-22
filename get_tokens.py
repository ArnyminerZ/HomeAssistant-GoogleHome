# Get tokens for Google Home Foyer API
# https://gist.github.com/rithvikvibhu/952f83ea656c6782fbd0f1645059055d

# Modified by ArnyminerZ, for loading parameters from dotenv

from gpsoauth import perform_master_login, perform_oauth
from uuid import getnode as getmac
import os, sys

# Creds to use when logging in
USERNAME = os.getenv("GOOGLE_USERNAME")
PASSWORD = os.getenv("GOOGLE_PASSWORD")

# Optional Overrides (Set to None to ignore)
device_id = None
master_token = None
access_token = None

# Flags
VERBOSE = os.getenv("VERBOSE", "true") == "true"
DEBUG = os.getenv("DEBUG", "false") == "true" and VERBOSE

if USERNAME is None or PASSWORD is None and VERBOSE:
    print("USERNAME nor PASSWORD was not delcared on .env")
    print("Please, check README.md and follow the instructions there on how to prepare the system.")
    sys.exit(1)


def get_master_token(username, password, android_id):
    res = perform_master_login(username, password, android_id)
    if DEBUG:
        print(res)
    if 'Token' not in res and VERBOSE:
        print('[!] Could not get master token.')
        return None
    return res['Token']


def get_access_token(username, master_token, android_id):
    res = perform_oauth(
        username, master_token, android_id,
        app='com.google.android.apps.chromecast.app',
        service='oauth2:https://www.google.com/accounts/OAuthLogin',
        client_sig='24bb24c05e47e0aefa68a58a766179d9b613a600'
    )
    if DEBUG:
        print(res)
    if 'Auth' not in res and VERBOSE:
        print('[!] Could not get access token.')
        return None
    return res['Auth']


def _get_android_id():
    mac_int = getmac()
    if (mac_int >> 40) % 2:
        raise OSError("a valid MAC could not be determined."
                      " Provide an android_id (and be"
                      " sure to provide the same one on future runs).")

    android_id = _create_mac_string(mac_int)
    android_id = android_id.replace(':', '')
    return android_id


def _create_mac_string(num, splitter=':'):
    mac = hex(num)[2:]
    if mac[-1] == 'L':
        mac = mac[:-1]
    pad = max(12 - len(mac), 0)
    mac = '0' * pad + mac
    mac = splitter.join([mac[x:x + 2] for x in range(0, 12, 2)])
    mac = mac.upper()
    return mac


if not device_id:
    device_id = _get_android_id()

if VERBOSE:
    print('\n[*] Getting master token...')
if not master_token:
    master_token = get_master_token(USERNAME, PASSWORD, device_id)
if VERBOSE:
    print('[*] Master token:', master_token)

    print('\n[*] Getting access token...')
if not access_token:
    access_token = get_access_token(USERNAME, master_token, device_id)
if VERBOSE:
    print('[*] Access token:', access_token)

    print('\n[*] Done.')