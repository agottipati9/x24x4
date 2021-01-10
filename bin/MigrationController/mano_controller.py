#!/bin/python3
from http.server import BaseHTTPRequestHandler, HTTPServer

"""
TODO:
1. Start MANO server on ADB Node
2. Spin up clients on NUC7 and NUC8
3. Move nuc7 via attenuation -> Print RSRQ and RSRP has deteriorated
4. Print Spinning up new base station on MANO -> Send command to NUC8 -> Run LINUX command
5. Print triggering handover -> Slowly move base stations closer and wait till handover happens
6. Send NUC7 kill command
"""

import socketserver
import threading
import subprocess
import time
import requests

clients = {}
migrated = False


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        global migrated
        global clients

        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        self.data = str(self.request.recv(1024).strip(), "utf-8")
        print("{} wrote: {}".format(self.client_address[0], self.data))
        clients[self.data] = self.request

        # Likewise, self.wfile is a file-like object used to write back
        # to the client
        if self.data == 'target':
            # Move UE away from source BS
            # subprocess.Popen(["sudo", "/usr/local/bin/atten", "9", "4"])
            # subprocess.Popen(["sudo", "/usr/local/bin/atten", "10", "4"])
            # time.sleep(2)
            # subprocess.Popen(["sudo", "/usr/local/bin/atten", "9", "8"])
            # subprocess.Popen(["sudo", "/usr/local/bin/atten", "10", "8"])
            # time.sleep(3)
            # print('RSRQ and RSRP have deteriorated.')
            time.sleep(3)
            print('Threshold has been reached. Triggering migration process...')

            # Spin up target BS
            print('Spinning up new base station.')
            self.request.sendall("start".encode("utf-8"))
            time.sleep(40)
            print('New base station has been instantiated.')

            # Get source RNTI
            print('Retrieving UE Information...')
            resp = requests.get('http://localhost:9999/stats/enb/10000')
            rnti = resp.json()['eNB_config'][0]['UE']['ueConfig'][0]['rnti']
            print('Retrieved UE Information')

            # Setting up handover with FlexRAN
            print('Preparing Migration (Handover).')
            subprocess.Popen(["sudo", "curl", "-XPOST", "http://localhost:9999/rrc/x2_ho_net_control/enb/10000/1"])
            subprocess.Popen(["sudo", "curl", "-XPOST", "http://localhost:9999/rrc/x2_ho_net_control/enb/10001/1"])
            # subprocess.Popen(["sudo", "/usr/local/bin/atten", "15", "1"])
            # subprocess.Popen(["sudo", "/usr/local/bin/atten", "16", "1"])
            time.sleep(5)
            print('Ready for Migration (Handover).')
            print('Triggering Migration (Handover).')
            url = "http://localhost:9999/rrc/ho/senb/10000/ue/{}/tenb/10001".format(rnti)
            subprocess.Popen(["sudo", "curl", "-XPOST", url])
            time.sleep(10)
            migrated = True
            print('Successful Migration. (Handover)')
        elif self.data == 'source' and migrated:
            # Remove source BS
            print('Removing old base station instance.')
            # request = clients["7"]
            self.request.sendall("kill".encode("utf-8"))
            time.sleep(1)
            print('Old base station has been removed. Exiting...')
            exit(0)
        elif self.data == 'source':
            self.request.sendall("no".encode("utf-8"))


if __name__ == "__main__":
    HOST, PORT = "10.10.1.3", 7777

    # Create the server, binding to localhost on port 9999
    server = socketserver.ThreadingTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        print('Listening on {}:{}'.format(HOST, PORT))
        server.serve_forever()
