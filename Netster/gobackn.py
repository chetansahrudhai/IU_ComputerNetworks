from typing import BinaryIO
import socket 
import pickle
import time

#References
#1. https://en.wikipedia.org/wiki/Go-Back-N_ARQ
#2. https://www.tutorialspoint.com/a-protocol-using-go-back-n

def gbn_server(iface: str, port: int, fp: BinaryIO) -> None:
    # Get address information for the server socket
    get_address_info = socket.getaddrinfo(iface, port, family=socket.AF_INET, proto=socket.IPPROTO_UDP)
    
    # Create a UDP socket for the server
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Extract server name and port from address information
    name_srvr = get_address_info[0][4][0]
    s_port = get_address_info[0][4][1]
    
    # Bind the server socket to the specified address and port
    socket_server.bind((name_srvr, s_port))
    
    # Initialize variables
    cont = b''  # Variable to store the received data
    expected_pck = 0  # Expected sequence number of the next packet
    sq_lst = []  # List to keep track of received sequence numbers
    flag = True  
    
    # Server loop to receive and process packets
    while flag:
        time_out = 0.07
        time_start = time.time()
        
        # Loop to handle packet reception within a timeout period
        while time.time() < time_start + time_out:
            # Receive data from the client
            datacontent, clnt_addr = socket_server.recvfrom(256)
            datacontent = pickle.loads(datacontent)
            
            # Check if the received packet has the expected sequence number
            if datacontent['seq_no'] == expected_pck and datacontent['length'] == len(datacontent['msg']):
                sq_lst.append(datacontent["seq_no"])
                
                # Prepare and send acknowledgment (ACK) for the received packet
                dix_ack = {"seq_no": expected_pck, "msg": "ACK"}
                ack_packet = pickle.dumps(dix_ack)
                socket_server.sendto(ack_packet, clnt_addr)
                
                # If the received message is an end signal, exit the loop
                if len(datacontent['msg']) <= 0:
                    flag = False
                    break
                
                # Append the data to the content variable
                cont += datacontent['msg']
                expected_pck += 1
            else:
                # Prepare and send negative acknowledgment (NACK) for the out-of-sequence packet
                dix_ack = {"seq_no": expected_pck - 1, "msg": "ACK"}
                ack_packet = pickle.dumps(dix_ack)
                socket_server.sendto(ack_packet, clnt_addr)
    
    # Write the accumulated data to the file and close the file
    fp.write(cont)
    fp.close()
    
    # Close the server socket
    socket_server.close()



def gbn_client(host: str, port: int, fp: BinaryIO) -> None:
    # Get address information for the client socket
    get_address_info = socket.getaddrinfo(host, port, family=socket.AF_INET, proto=socket.IPPROTO_UDP)
    
    # Extract server name and port from address information
    name_srvr = get_address_info[0][4][0]
    s_port = get_address_info[0][4][1]
    
    # Create a UDP socket for the client
    clnt_sokt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clnt_sokt.settimeout(0.1)  # Set a timeout for the client socket
    
    # Read the content of the file to be sent
    cont = fp.read()
    chunk_size = 100  # Size of each data chunk to be sent
    count = 0  # Counter for sequence numbers
    cont_lst = []  # List to store data chunks with sequence numbers
    
    # Divide the content into chunks with sequence numbers
    for i in range(0, len(cont), chunk_size):
        chunk = cont[i:i + chunk_size]
        dict1 = {"seq_no": count, "msg": chunk, "length": len(chunk)}
        count += 1
        cont_lst.append(dict1)
    
    # Add an end signal packet to the list
    dict1 = {"seq_no": count, "msg": '', "length": 0}
    cont_lst.append(dict1)
    
    total_windows = len(cont_lst)  # Total number of windows
    windows_size = total_windows // 2  # Initial window size
    cnt = 0  # Counter for tracking sent packets
    flag = True  # Flag to control the loop
    
    # Client loop to send and receive packets
    while cnt < total_windows:
        strt = cnt  # Starting index of the current window
        tmp = []  # Temporary list to store sent packet indices within the window
        
        # Loop to send packets within the current window size
        for i in range(1, windows_size + 1):
            try:
                # Send the packet to the server
                pkt = cont_lst[cnt]
                packet = pickle.dumps(pkt)
                clnt_sokt.sendto(packet, (name_srvr, s_port))
                tmp.append(cnt)
                cnt += 1
                
                # Break if all packets have been sent
                if cnt >= total_windows:
                    flag = False
                    break
            except socket.timeout:
                continue
        
        # Receive acknowledgment from the server
        try:
            test, addr = clnt_sokt.recvfrom(256)
            test = pickle.loads(test)
            seq_no = test['seq_no']
            
            # Break if the end signal is received
            if seq_no == total_windows - 1:
                break
            
            # Update window size if the acknowledgment is received for the expected packet
            if seq_no == cnt:
                windows_size += 1
                cnt = seq_no + 1
            else:
                cnt = seq_no + 1
        except socket.timeout:
            # Reduce window size on timeout
            windows_size = max(1, int(windows_size * 0.5))
            cnt = strt  # Reset the counter to the starting index of the current window