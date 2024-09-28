from typing import BinaryIO
from struct import Struct, unpack
import socket


# Explain the structure of an RUDP packet.
struct_rudp = Struct('!HHH')
rudp_head_size = struct_rudp.size

def stopandwait_server(iface:str, port:int, fp:BinaryIO) -> None:
    
    # Set up the sequence pattern for the packets that alternate
    seq = 0
    
    # Make a UDP socket and bind it to the designated port and interface
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((iface, port))
    
    i = 0
    while i < 200:
        # Obtain RUDP packets from your client
        data, client_address = server_socket.recvfrom(64)

        # Parse the RUDP packet
        if len(data) >= rudp_head_size:
            s_num, msg, d_lnt = struct_rudp.unpack(data[:rudp_head_size])

            if msg == 2:
                # End signal received, break the loop
                break

            data_pack = data[rudp_head_size:]

            if msg == 0 and s_num == seq:
                # Write data to the file
                fp.write(data_pack) 
                
                # Prepare and send acknowledgment (ACK)
                ack_packet = struct_rudp.pack(s_num, 1, 0)
                server_socket.sendto(ack_packet, client_address)

                # Toggle the sequence pattern for the next expected packet
                seq ^= 1
              
            else:
                # Resend ACK for the previous sequence if received out of order
                if s_num == seq^1:
                    ack_packet = struct_rudp.pack(s_num, 1, 0)
                    server_socket.sendto(ack_packet, client_address)
                

    # Close the server socket
    server_socket.close()

def stopandwait_client(host:str, port:int, fp:BinaryIO) -> None:
    
    # Set the sequence number for the packets that alternate.
    c_seq = 0
    
    # Create a RUDP socket for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (host, port)

    while True:
        # Read data from the file in chunks
        chunk = fp.read(16)

        if not chunk:
            # If no more data to send, send an end signal and break the loop
            signal_endl = struct_rudp.pack(c_seq, 2, 0)
            s_num, msg, d_lnt = struct_rudp.unpack(signal_endl[:rudp_head_size])
            client_socket.sendto(signal_endl, server_address)
            break  

        # Create and send RUDP packet
        pack_rudp = struct_rudp.pack(c_seq, 0, len(chunk)) + chunk

        while True:
            # Send the RUDP packet to the server
            client_socket.sendto(pack_rudp, server_address)

            # Set a timeout for receiving ACK
            client_socket.settimeout(0.07)

            try:
                # Receive ACK from the server
                ack_packet, _ =  client_socket.recvfrom(1024)
                ack_seq, ack_mssg, _ = struct_rudp.unpack(ack_packet)

                if ack_mssg == 1 and ack_seq == c_seq:
                    # After receiving the packet's ACK, proceed to the next sequence number.
                    c_seq ^= 1  # Alternating bit (0 or 1)
                    break
                elif ack_mssg == 1 and ack_seq != c_seq:
                    # Ignore out-of-order ACK and continue waiting
                    continue
            except socket.timeout:
                # For timeout probs
                continue

    # Close the client socket
    client_socket.close()