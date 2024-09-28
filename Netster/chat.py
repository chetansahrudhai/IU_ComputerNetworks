from ast import arg
import socket
import sys
import threading
import select

# Count of total clients connected so far for TCP
num_connected_clients = 0
# List of all connected clients for TCP
connected_clients = []
# A flag to track if the server is still running for TCP multithreading
is_server_running = True
server_tcp_socket = ''
# Default messages to reply to clients
default_messages = {"hello\n": "world\n", "goodbye\n": "farewell\n", "exit\n": "ok\n"}

def handle_client(client_socket, client_address):
    global num_connected_clients, connected_clients, is_server_running, default_messages
    sys.stdout.write(f"Connection {str(num_connected_clients)} from {client_address[0], client_address[1]}")
    sys.stdout.write("\n")
    num_connected_clients += 1
    message_from_client = ""
    
    while is_server_running:
        message_from_client = client_socket.recv(256)
        
        if message_from_client:
            sys.stdout.write(f"Received message from {client_address[0], client_address[1]}")
            sys.stdout.write("\n")
        
        message_from_client = message_from_client.decode() 
        
        if message_from_client in default_messages.keys():
            reply_message = default_messages[message_from_client]
        else:
            reply_message = message_from_client
        
        client_socket.send(reply_message.encode())
        
        if message_from_client == "goodbye\n" or message_from_client == "exit\n":
            break
    
    client_socket.close()
    
    if message_from_client == "exit\n":
        is_server_running = False

def server_thread():
    global server_tcp_socket, is_server_running, connected_clients
    while is_server_running:
        client_socket, client_address = server_tcp_socket.accept()
        new_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        new_thread.daemon = True
        new_thread.start()
        connected_clients.append([client_socket, client_address])
    
    server_tcp_socket.close()
    sys.exit()

def chat_server(interface:str, port:int, use_udp:bool) -> None:
    if use_udp:
        global default_messages
        interface_info = socket.getaddrinfo(interface, port)
        ipv4_udp_address = ""
        _, _, _, _, ipv4_udp_address = interface_info[1]
        server_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_udp_socket.bind(ipv4_udp_address)
        sys.stdout.write("Hello, I am a server")
        sys.stdout.write("\n")
        
        while True:
            message_from_client, client_address = server_udp_socket.recvfrom(256)
            sys.stdout.write(f"Received message from {client_address[0], client_address[1]}")
            sys.stdout.write("\n")
            message_from_client = message_from_client.decode()
            reply_message = ""
            
            if message_from_client in default_messages.keys():
                reply_message = default_messages[message_from_client]
            else:
                reply_message = message_from_client
            
            reply_message = reply_message.encode()
            server_udp_socket.sendto(reply_message, client_address)
            
            if message_from_client == "exit\n":
                sys.exit()
    elif not use_udp:
        global server_tcp_socket, is_server_running, connected_clients
        interface_info = socket.getaddrinfo(interface, port)
        ipv4_tcp_address = ""
        _, _, _, _, ipv4_tcp_address = interface_info[0]
        server_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sys.stdout.write("Hello, I am a server")
        sys.stdout.write("\n")
        server_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_tcp_socket.bind(ipv4_tcp_address)
        server_tcp_socket.listen()
        
        server_thread_handler = threading.Thread(target=server_thread, args=())
        server_thread_handler.daemon = True
        server_thread_handler.start()
        
        while is_server_running:
            continue
        
        for client_info in connected_clients:
            try:
                client_socket = client_info[0]
                client_socket.close()
            except:
                continue
        
        sys.exit()

def chat_client(host:str, port:int, use_udp:bool) -> None:
    client_address_info = socket.getaddrinfo(host, port)
    
    if use_udp:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    elif not use_udp:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(client_address_info[0][4])
    
    sys.stdout.write("Hello, I am a client")
    sys.stdout.write("\n")
    last_sent_message = ""
    
    while True:
        send_server_message = input() + "\n"
        last_sent_message = send_server_message
        send_server_message = send_server_message.rstrip()
        send_server_message = send_server_message.lstrip()
        
        if len(send_server_message) > 256:
            send_server_message = send_server_message[0:255]
            send_server_message += "\n"
        
        send_server_message += "\n"
        
        if not use_udp:
            client_socket.send(send_server_message.encode())
            response_from_server = client_socket.recv(256)
        elif use_udp:
            client_socket.sendto(send_server_message.encode(), client_address_info[0][4])
            response_from_server, _ = client_socket.recvfrom(256)
        
        response_from_server = response_from_server.decode()
        print(response_from_server, end="")
        
        if (last_sent_message == "goodbye\n" and response_from_server == "farewell\n") or \
           (last_sent_message == "exit\n" and response_from_server == "ok\n"):
            sys.exit()