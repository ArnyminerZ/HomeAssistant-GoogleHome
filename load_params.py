# Loads all the parameters from the command line

import sys, getopt

device_ip = None
device_name = None
try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:n:",["ip=","name="])
except getopt.GetoptError:
    print('get_alarms.py -i <device-ip> -n <device-name>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print ('get_alarms.py -i <device-ip> -n <device-name>')
        sys.exit()
    elif opt in ("-i", "--ip"):
        device_ip = arg
    elif opt in ("-n", "--name"):
        device_name = arg