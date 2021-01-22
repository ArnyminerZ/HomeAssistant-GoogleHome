# Loads all the parameters from the command line

import sys, getopt

device_ip = None
device_name = None
fetch_path = None
output_param = None
use_json = False
try:
    opts, args = getopt.getopt(sys.argv[1:],"hji:n:p:o:",["ip=","name=","path=","output="])
except getopt.GetoptError:
    print('ghome_get.py [-h] [-j] <device-ip> -n <device-name> -p <path> -o [output]')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print ('ghome_get.py [-h] [-j] -i <device-ip> -n <device-name> -p <path> -o [output]')
        sys.exit()
    elif opt == '-j':
        use_json = True
    elif opt in ("-i", "--ip"):
        device_ip = arg
    elif opt in ("-n", "--name"):
        device_name = arg
    elif opt in ("-p", "--path"):
        fetch_path = arg
    elif opt in ("-o", "--output"):
        output_param = arg