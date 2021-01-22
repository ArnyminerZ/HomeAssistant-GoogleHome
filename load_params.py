# Loads all the parameters from the command line

import sys, getopt

device_ip = None
device_name = None
fetch_path = None
try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:n:p:",["ip=","name=","path="])
except getopt.GetoptError:
    print('ghome_get.py -i <device-ip> -n <device-name> -p <path>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print ('ghome_get.py -i <device-ip> -n <device-name> -p <path>')
        sys.exit()
    elif opt in ("-i", "--ip"):
        device_ip = arg
    elif opt in ("-n", "--name"):
        device_name = arg
    elif opt in ("-p", "--path"):
        fetch_path = arg