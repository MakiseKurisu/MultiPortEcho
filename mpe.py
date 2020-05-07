#!/usr/bin/env python3

import sys
import getopt
import socket
import select

RETURN_SUCCESS = 0
RETURN_MISSING_ARGUMENT = 1
RETURN_NO_PORT_AVAILABLE = 2
RETURN_TOO_MANY_PORTS = 3

def inclusive_range(start, end, step = 1):
    return range(start, end + 1, step)

def main():
    server_mode = False
    port_low = 0
    port_high = 0
    server_address = ""

    timeout = 1.0
    echo_magic = "mpe"
    encoding = "utf-8"
    receive_buffer_size = 4096
    binding_interface = "0.0.0.0"

    try:
        if len(sys.argv) == 1:
            raise getopt.GetoptError("help")
        opts, _ = getopt.getopt(sys.argv[1:], "sa:l:h:")
    except getopt.GetoptError:
        print("mpe.py [-s|-a <address>] -l <port_low> -h <port_high>")
        print("-s: running in server mode")
        return RETURN_MISSING_ARGUMENT

    for opt, arg in opts:
        if opt == "-s":
            server_mode = True
        elif opt == "-l":
            port_low = int(arg)
        elif opt == "-h":
            port_high = int(arg)
        elif opt == "-a":
            server_address = arg
    
    if server_mode:
        socket_list = []
        for port in inclusive_range(port_low, port_high):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.bind((binding_interface, port))
                socket_list.append(s)
            except PermissionError as e:
                if e.errno == 13:
                    print("Do not have enough permission to open port", port, ". Skip.")
                else:
                    raise
            except OSError as e:
                if e.errno == 98:
                    print("Port", port, "is already opened by another process. Skip.")
                elif e.errno == 24:
                    print("Too many ports are opened. Please reduce the range and try again.")
                    return RETURN_TOO_MANY_PORTS
                else:
                    raise

        if len(socket_list) == 0:
            print("No port is available. Quit.")
            return RETURN_NO_PORT_AVAILABLE

        print("Listening...")
        while True:
            try:
                ready, _, _ = select.select(socket_list, [], [])
                for s in ready:
                    _, port = s.getsockname()
                    print("Receiving connection at port", port)
                    data, addr = s.recvfrom(receive_buffer_size)
                    s.sendto(data, addr)
            except ValueError as e:
                if str(e) == "filedescriptor out of range in select()":
                    print("Too many ports are opened. Please reduce the range and try again.")
                    return RETURN_TOO_MANY_PORTS
                break
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(timeout)
        for port in inclusive_range(port_low, port_high):
            try:
                print("Testing port", port, "...", end = '\r')
                s.sendto(echo_magic.encode(encoding), (server_address, port))
                data, _ = s.recvfrom(receive_buffer_size)
                if data.decode(encoding) == echo_magic:
                    print("Port", port, "is open.")
            except socket.timeout:
                pass
        s.close()

    return RETURN_SUCCESS

if __name__ == "__main__":
    sys.exit(main())