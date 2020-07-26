import socket
import sys
import _thread
import time
import numpy as np
import networkx as nx
from networkx.generators.random_graphs import erdos_renyi_graph
import matplotlib.pyplot as plt
import pickle
time.sleep(3)
f = open('store.pckl', 'rb')
G = pickle.load(f)
f.close()                                   ## LOADs the graph


def handleConnections(id,nodes):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port_no=10000+id
    print("\n"+str(port_no)+"\n")
    server_address = ('localhost', port_no)
    print(sys.stderr, 'starting up on %s port %s' % server_address)
    sock.bind(server_address)
    sock.listen(5)
    rp_sender__seq = []
    while True:
        # Wait for a connection
        print (sys.stderr, 'waiting for a connection')
        connection, client_address = sock.accept()
        try:
            print(sys.stderr, 'connection from', client_address)
            # Receive the data in small chunks and retransmit it
            data = connection.recv(200).decode()

            print("Data recieved: ",data,'\n')
            if data=="G-C":
                print("G-CG-CG-C")

                f = open('store.pckl', 'rb')
                G = pickle.load(f)
                print(list(G.edges))
                f.close()
                continue
            recieved=False
            recieved_packet=to_Packet(data)
            print_packet(recieved_packet)
            rp_index=getIndex_2d(rp_sender__seq,recieved_packet.sender)
            print("\nRecieved packets . In every array first index tells the sender and the next elements tells the seq_no recieved")
            print_2d(rp_sender__seq)
            sendInfo=str(id)+" recieved Packet(sender:"+recieved_packet.sender+":destination:"+recieved_packet.destination+":seq_no:"+str(recieved_packet.sequence_number)+"prev_node"+recieved_packet.previous_node+")"
            if rp_index==-1:
                print("Sender ",recieved_packet.sender," not find")
                rp_sender__seq.append([recieved_packet.sender])
                rp_sender__seq[len(rp_sender__seq)-1].append(recieved_packet.sequence_number)
                print("\nRecieved packets after")
                print_2d(rp_sender__seq)
            else:
                print("Sender exists\n")
                rp_seqno_exists=getIndex_1d(rp_sender__seq[rp_index],recieved_packet.sequence_number)

                if rp_seqno_exists==-1:
                    print("\nSeq-no doesnot exist")
                    rp_sender__seq[rp_index].append(recieved_packet.sequence_number)
                    print("\nAdded seq-no, Updated recived packets\n")
                    print_2d(rp_sender__seq)
                else:
                    print("Already Recieved")
                    sendInfo+=" (Already recieved packet) "
                    sendtoServer(sendInfo)

                    recieved=True

            if id==int(recieved_packet.destination) and recieved==False:
                sendInfo+=" (Destination reached) "
                sendtoServer(sendInfo)
                print("\nDestination reached\n")


            elif recieved==False:
                print("Forwarding packet to neighbors to neighbors")
                sendPackets(recieved_packet,nodes,id)





        finally:
            # Clean up the connection
            connection.close()

def sendtoServer(inp_string):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 9000)
    sock.connect(server_address)
    try:
        sock.send(inp_string.encode())
    finally:
        print(sys.stderr, 'closing socket')
        sock.close()

def sendPackets(input,nodes,my_id):         #(packet,total_nodes_of_the_network,my_id)
    id=my_id
    neighbors = list(G.neighbors(id))           #list of neibs of id
    if input.previous_node!="":
        print("pn",int(input.previous_node))        # remove previous nodes edge.
        neighbors.remove(int(input.previous_node))  #dont send recieved packet to sender

    sendInfo=str(my_id)+" is sending Packet (sender:"+input.sender+":destination:"+input.destination+":seq_no:"+str(input.sequence_number)+"prev_node"+input.previous_node+") to"
    neighborstr = ' '.join([str(elem) for elem in neighbors])
    sendInfo+=neighborstr
    sendtoServer(sendInfo)
    print("\nMy neighbors are ",neighbors,'\n')
    i=0
    while i < nodes:
        if ((i!=id) and (i in neighbors)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect the socket to the port where the server is listening
            port_no=10000+i
            server_address = ('localhost', port_no)
            print(sys.stderr, 'connecting to %s port %s' % server_address)
            sock.connect(server_address)
            try:
                # Send data
                input.previous_node=str(my_id)
                message = input.to_String()
                print(sys.stderr, 'sending "%s"' % message)
                sock.send(message.encode())
            finally:
                print(sys.stderr, 'closing socket')
                sock.close()
        i+=1


class Packet:
    packet_type=""
    sequence_number=0
    message=""
    sender=""
    destination=""
    loc_x=0.0           #irrelevant
    loc_y=0.0            #irrelevant
    previous_node=""
    def __init__(self, packet_, id,message, sender,destination,loc_x,loc_y,prev):
        self.packet_type=packet_
        self.sequence_number=id
        self.message = message
        self.sender = sender
        self.destination=destination
        self.loc_x=loc_x
        self.loc_y=loc_y
        self.previous_node=prev
    def to_String(self):
        packet_string=self.packet_type+','+str(self.sequence_number)+','+self.message+','+self.sender+','+self.destination+','+str(self.loc_x)+','+str(self.loc_y)+','+self.previous_node
        return packet_string


def to_Packet(packet_string):
    split_information = packet_string.split(',')
    return Packet(split_information[0],int(split_information[1]),split_information[2],split_information[3],split_information[4],split_information[5],split_information[6],split_information[7])

def getIndex_2d(array,value):
    if len(array)!=0:
        i=0
        while i<len(array):
            if array[i][0]==value:
                return i
            i+=1
        return -1
    else:
        return -1
def getIndex_1d(array,value):
    if len(array)!=0:
        i=0
        while i<len(array):
            if array[i]==value:
                return i
            i+=1
        return -1
    else:
        return -1
def print_2d(array):
    i=0
    j=0
    while i<len(array):
        print("[")
        while j<len(array[i]):
            print(array[i][j])
            j+=1
        i+=1
        print("]")
def print_packet(packet):
    print("\nPacket Details \nPacketType:",packet.packet_type," SequenceNo:",packet.sequence_number," Message",packet.message)
    print("Sender", packet.sender," Destination",packet.destination," Previous Node:",packet.previous_node,"\n")
if __name__ == "__main__":
#    time.sleep(3)
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")

    my_id=int(sys.argv[1])

    loc_x=sys.argv[2]
    loc_x=float(loc_x[:4])
    loc_y=sys.argv[3]
    loc_y=float(loc_y[:4])


    nodes=int(sys.argv[4])
    port_no=10000+my_id
    print("Port_nos",port_no,'\n')
    _thread.start_new_thread(handleConnections, (my_id,nodes))
    print("N")
    print(G.nodes)
    print("e")
    print(G.edges)
    seq_no=0
    while True:
        print("SendDatatoSomeone\nEnter Dest")
        dest = input()
        print("Enter your message\n")
        message = input()
        if dest!="" and message!="":
            packet=Packet("F",seq_no,message,str(my_id),str(dest),str(loc_x),str(loc_y),"")
            sendPackets(packet,nodes,my_id)
            seq_no+=1
    # Create a TCP/IP socket




"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 9000)
    print(sys.stderr, 'connecting to %s port %s' % server_address)
    sock.connect(server_address)
    try:
        # Send data
        message = 'This is the message.  It will be repeated.'
        print(sys.stderr, 'sending "%s"' % message)
        sock.send(message.encode())
        # Look for the response
        amount_received = 0
        amount_expected = len(message)
        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print(sys.stderr, 'received "%s"' % data)
    finally:
        print(sys.stderr, 'closing socket')
        sock.close()
"""


