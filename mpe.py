#!/usr/bin/env python3

import sys
import getopt
import socket
import select

def main():
    server_mode = False
    port_low = 0
    port_high = 0
    server_address = ""

    echo_magic = "mpe"
    encoding = "utf-8"
    receive_buffer_size = 4096
    binding_interface = "0.0.0.0"

    try:
        if len(sys.argv) == 1:
            raise getopt.GetoptError("help")
        opts, _ = getopt.getopt(sys.argv,"sa:l:h:")
    except getopt.GetoptError:
        print("mpe.py [-s|-a <address>] -l <port_low> -h <port_high>")
        print("-s: running in server mode")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-s":
            server_mode = True
        elif opt == "-l":
            port_low = arg
        elif opt == "-l":
            port_high = arg
        elif opt == "-a":
            server_address = arg
    
    if server_mode:
        socket_list = []
        for port in range(port_low, port_high):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind((binding_interface, port))
            socket_list.append(s)

        print("Listening from ", port_low, " to ", port_high, "...")
        while True:
            ready, _, _ = select.select(socket_list, [], [])
            for s in ready:
                data, addr = s.recvfrom(receive_buffer_size)
                s.sendto(data, addr)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for port in range(port_low, port_high):
            s.sendto(echo_magic.encode(encoding), (server_address, port))
            data, _ = s.recvfrom(receive_buffer_size).decode(encoding)
            if data == echo_magic:
                print("Port ", port, " is open.")
        s.close()

if __name__ == "__main__":
    main()