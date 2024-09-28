from pydoc import cli
from typing import BinaryIO
import socket
import sys

def file_server(iface:str, port:int, use_udp:bool, fp:BinaryIO) -> None:
    # Get address information for the specified interface and port
    iface_info = socket.getaddrinfo(iface, port)
    ipv4_addr = ""
    universal_socket = ""
    
    # Print a server hello message
    sys.stdout.write("Hello, I am a server")
    sys.stdout.write("\n")
    
    if not use_udp:
        ipv4_addr = ""
        # Extract IPv4 address from the address info
        _, _, _, _, ipv4_addr = iface_info[0]
        
        # Create a TCP socket and set socket options
        universal_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        universal_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind the socket to the IPv4 address
        universal_socket.bind(ipv4_addr)
        
        # Listen for incoming connections
        universal_socket.listen()
        conn, _ = universal_socket.accept()
        
        while True:
            # Receive data from the client
            data_from_client = conn.recv(256)
            if data_from_client:
                # Write the received data to the BinaryIO stream
                fp.write(data_from_client)
            else:
                # Close the connection and the BinaryIO stream when done
                conn.close()
                fp.close()
                break
        
        # Close the server socket
        universal_socket.close()
    else:
        ipv4_addr = ""
        # Extract IPv4 address from the address info
        _, _, _, _, ipv4_addr = iface_info[1]

        # Create a UDP socket and set socket options
        universal_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        universal_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind the socket to the IPv4 address
        universal_socket.bind(ipv4_addr)
        
        while True:
            # Receive data from the client in UDP mode
            data_from_client, _ = universal_socket.recvfrom(256)
            if data_from_client:
                # Write the received data to the BinaryIO stream
                fp.write(data_from_client)
            else:
                # Close the BinaryIO stream when done
                fp.close()
                break
        
        # Close the server socket
        universal_socket.close()
    
    # Exit the program
    sys.exit()

def file_client(host:str, port:int, use_udp:bool, fp:BinaryIO) -> None:
    # Print a client hello message
    sys.stdout.write("Hello, I am a client")
    sys.stdout.write("\n")
    
    # Get address information for the specified host and port
    client_addr_info = socket.getaddrinfo(host, port)
    
    if not use_udp:
        # Create a TCP socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(client_addr_info[0][4])
    elif use_udp:
        # Create a UDP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Read data from the BinaryIO stream
    data_to_server = fp.read()
    size = len(data_to_server)
    start = 0
    
    for x in range(int(size / 256)):
        start = x * 256
        if not use_udp:
            # Send data to the server in TCP mode
            client_socket.send(data_to_server[start:start+256])
        elif use_udp:
            # Send data to the server in UDP mode
            client_socket.sendto(data_to_server[start:start+256], client_addr_info[0][4])
    
    if start > 0:
        start += 256
    
    if not use_udp:
        # Send the remaining data and a closing signal in TCP mode
        client_socket.send(data_to_server[start:])
        client_socket.send(b'')
    elif use_udp:
        # Send the remaining data and a closing signal in UDP mode
        client_socket.sendto(data_to_server[start:], client_addr_info[0][4])
        client_socket.sendto(b'', client_addr_info[0][4])
    
    # Close the BinaryIO stream and the client socket
    fp.close()
    client_socket.close()
    
    # Exit the program
    sys.exit()