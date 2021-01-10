#!/usr/bin/python3.6
"""
TODO:
1. Attach to Mano_Controller
2. Receive command and execute
   - Nuc7 kill command remove base station -> sudo pkill -f srsenb
   - Nuc8 start command and init base station -> sudo ~/srsLTE/build/srsenb/src/srsenb ~/.config/srslte/enb.conf
     - pipe to stdout
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import time

import socket
import sys
import subprocess
import time

HOST, PORT = "10.10.1.3", 7777
timeout = 5
id = sys.argv[1].split()

# Timeout
if len(id) == 3 and id[1] == '-t':
    timeout = sys.argv[2] if sys.argv[2].isnumeric() else 5
id = id[0]

# Create a socket (SOCK_STREAM means a TCP socket)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(bytes(id + "\n", "utf-8"))
    print("Sent:     {}".format(id))

    while True:
        # Receive data from the server
        received = str(sock.recv(1024), "utf-8")
        if len(received) > 0:
            if received == 'kill':
                print("Received: {}".format(received))
                time.sleep(timeout)
                subprocess.call(["sudo", "pkill", "-f", "lte-softmodem.R"])
                print("Terminated base station instance.")
                # exit(0)
            elif received == 'start':
                print("Received: {}".format(received))
                exit(0)
                # # cmd = subprocess.Popen(["sudo", "/users/agot/srsLTE/build/srsenb/src/srsenb",
                # #                         "/users/agot/.config/srslte/enb.conf"], stdout=subprocess.PIPE)
                # cmd = subprocess.Popen(["sudo", "/users/agot/start.sh"], stdout=subprocess.PIPE)
                # print("Instantiated new base station instance.")
                # # while True:
                # #     while not cmd.poll():
                # #         f.flush()
                # while not cmd.poll():
                #     line = cmd.stdout.readline()
                #     if not line:
                #         break
            elif received == 'no':
                time.sleep(15)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((HOST, PORT))
                sock.sendall(bytes(id + "\n", "utf-8"))