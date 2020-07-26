import socket
import sys
import _thread
import time
from random import seed
from datetime import datetime

import numpy as np
import networkx as nx
from networkx.generators.random_graphs import erdos_renyi_graph
import matplotlib.pyplot as plt
from random import randint
import random
import pickle
import time
time.sleep(3)
f = open('store.pckl', 'rb')
G = pickle.load(f)
f.close()

Routes=[]
seq_no=0



def handleConnections(id,nodes):
    global G

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    seed(1)
    port_no=10000+id
    print("\n"+str(port_no)+"\n")
    server_address = ('localhost', port_no)
    print(sys.stderr, 'starting up on %s port %s' % server_address)
    sock.bind(server_address)
    sock.listen(20)
    rp_sender__seq = []
    while True:
        # Wait for a connection
        print (sys.stderr, 'waiting for a connection')
        random.seed(datetime.now())
        connection, client_address = sock.accept()
        try:
            print(sys.stderr, 'connection from', client_address)
            # Receive the data in small chunks and retransmit it
            data = connection.recv(200).decode()
            j=False
            print("Data recieved: ",data,'\n')
            recieved=False
            if data=="G-C":
                print("G-CG-CG-C")

                f = open('store.pckl', 'rb')
                G = pickle.load(f)
                print(list(G.edges))
                f.close()

                continue
            value=randint(1,100)
            print("Val"+str(value))
            if value<25:
                print("Packet Dropped")
                sendtoServer("PD")
                continue

            recieved_packet=to_Packet(data)
            print_packet(recieved_packet)

            if recieved_packet.packet_type == "RERR":
                print_packet(recieved_packet)
                if recieved_packet.pathNow.split("-")[1] == str(my_id):
                    print("RRER reached to dest")
                    packet_split=recieved_packet.message.split("RERR")
                    removePath(packet_split[1])
                    recieved_packet.message=packet_split[0]
                    recieved_packet.packet_type="RREQ"
                    recieved_packet.previous_node=""
                    recieved_packet.pathNow=""
                    sendPackets(recieved_packet,nodes,id)

                else:
                    packet_split = recieved_packet.message.split("RERR")
                    removePath(packet_split[1])
                    split_ = recieved_packet.pathNow.split("-")
                    i = 1
                    loc = -1
                    print("Len", split_)
                    while i < len(split_):
                        if split_[i] == str(my_id):
                            loc = i - 1
                            break
                        i += 1
                    print("Loc", loc)
                    sendRRep(recieved_packet, split_[loc], my_id)
            elif recieved_packet.packet_type=="DATA":
                print("Recieved First Data")
                if recieved_packet.destination==str(my_id):
                    sendtoServer("PR")
                    path=""
                    print("Data reached to dest R-added"+"-"+recieved_packet.pathNow[::-2])
                    spl=recieved_packet.pathNow.split("-")
                    i=len(spl)-1
                    while i>=1:
                        path+="-"+spl[i]
                        i-=1


                    Routes.append(path)

                else:
                    split_=recieved_packet.pathNow.split("-")
                    i=1
                    loc=-1
                    print("Len",split_)
                    while i<len(split_):
                        if split_[i]==str(my_id):
                            loc=i+1
                            break
                        i+=1
                    print("Loc",loc)
                    sendRRep(recieved_packet,split_[loc],my_id)

            elif recieved_packet.packet_type=="RREP":
                print_packet(recieved_packet)
                if recieved_packet.pathNow.split("-")[1]==str(my_id):
                    print("RREP reached to dest")
                    Routes.append(recieved_packet.pathNow)
                    InitiateDataPacket(my_id,recieved_packet)


                else:
                    new_path = recieved_packet.pathNow
                    new_path=new_path[new_path.index(str(my_id)):]
                    new_path = "-" + new_path
                    print(new_path)
                    addRoute(new_path)
                    print("New path discoverd", new_path)
                    split_=recieved_packet.pathNow.split("-")
                    i=1
                    loc=-1
                    print("Len",split_)
                    while i<len(split_):
                        if split_[i]==str(my_id):
                            loc=i-1
                            break
                        i+=1
                    print("Loc",loc)

                    sendRRep(recieved_packet,split_[loc],my_id)

            elif recieved_packet.packet_type=="RREQ":
                rp_index=getIndex_2d(rp_sender__seq,recieved_packet.sender)
                print("\nRecieved packets . In every array first index tells the sender and the next elements tells the seq_no recieved")
                print_2d(rp_sender__seq)
                sendInfo=str(id)+" recieved Packet(sender:"+recieved_packet.sender+":destination:"+recieved_packet.destination+":seq_no:"+str(recieved_packet.sequence_number)+"prev_node"+recieved_packet.previous_node+")"
                if recieved_packet.sender==str(my_id):
                    print("I made this packet Recieved")
                    continue

                elif rp_index==-1:
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
                    #    new_path = recieved_packet.pathNow[::-1][:-1]
                        spl = recieved_packet.pathNow.split("-")
                        path = ""
                        i = len(spl) - 1
                        while i >= 1:
                            path += "-"+spl[i]
                            i-=1
##### 506     -3-6-0-5
                        new_path = "-" + str(my_id) + path
                        addRoute(new_path)
                        print("New path discoverd", new_path)
                        recieved=True

                if id==int(recieved_packet.destination) and recieved==False:
                    sendInfo+=" (Destination reached) "
                    sendtoServer(sendInfo)              #-5-0-2-4
                    path=recieved_packet.pathNow+'-'+str(my_id)
                    InitiateRREP(my_id,path,recieved_packet.message)
                    print("\nDestination reached\n")


                elif recieved==False:
                    if routeCheck(recieved_packet.destination)=="-1":
                        print("Forwarding packet to neighbors to neighbors")
    #                    new_path=recieved_packet.pathNow[::-1][:-1]
                        spl=recieved_packet.pathNow.split("-")
                        path=""
                        i=len(spl)-1
                        while i>=1:
                            path+="-"+spl[i]
                            i-=1
                        new_path="-"+str(my_id)+path
                        addRoute(new_path)
                        print("New path discoverd",new_path)
                        sendPackets(recieved_packet,nodes,id)
                    else:

                        spl = recieved_packet.pathNow.split("-")
                        path = ""
                        i = len(spl) - 1
                        while i >= 1:
                            path += "-" + spl[i]
                            i -= 1

                        new_path = "-" + str(my_id) + path
                        addRoute(new_path)
                        path=routeCheck(recieved_packet.destination)
                        InitiateRREP(my_id, recieved_packet.pathNow+path, recieved_packet.message)
                        print("PATH SENT WITHOUT REACHING DESTINATION")




        finally:
            # Clean up the connection
            connection.close()


def addRoute(route):

    global Routes
    if len(route)>4:
        print("Rt",route)
        i=0;
        b=False;
        while i< len(Routes):
            print("Nr:",route,"Rt:",Routes[i])
            if route in Routes[i]:
                print("AE")
                b=True
                break
            if route==Routes[i]:
                print("AE")
                b=True
                break
            i+=1
        if b==False:
            print("AD")
            Routes.append(route)

def removePath(path):
    global Routes
    i=0
    print("In_rp")
    while i<len(Routes):
        if path in Routes[i]:
            p_spl=path.split("-")
            Routes[i]=Routes[i].split(path)[0]+p_spl[0]
            print("Updated Path",Routes[i])
        i+=1
    print("Out_rp")

def routeCheck(dest):
    # [(-1-2-3-4),(-2-3-1-5)]
    if len(Routes)==0:
        return "-1"
    i=0
    foundroute=""
    foundroutes=[]
    sizes=[]
    while i<len(Routes):
        print("\n",Routes[i],"\n")
        subroute=Routes[i].split("-")
        j=1
        foundroute="-"
        while j<len(subroute):
            foundroute += subroute[j]
            if dest==subroute[j]:
                print("Discovered",foundroute)
                foundroutes.append(foundroute)
                sizes.append(len(foundroute))

#                return foundroute
            foundroute+='-'
            j+=1
        i+=1
    if len(sizes)==0:
        return "-1"
    elif len(sizes)==1:
        return foundroutes[0]
    else:
        minpos = sizes.index(min(sizes))
        return foundroutes[minpos]

    return "-1"
def sendDataPacket(my_id,r_packet):
    path_split=r_packet.pathNow.split("-")
    to_send_id=int(path_split[2])
    if findIfExists(my_id, to_send_id) == 1:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        port_no = 10000 + to_send_id
        server_address = ('localhost', port_no)
        print(sys.stderr, 'connecting to %s port %s' % server_address)
        sock.connect(server_address)
        try:
            # Send data
            r_packet.previous_node=str(my_id)
            message = r_packet.to_String()
            print(sys.stderr, 'sending "%s"' % message)
            sock.send(message.encode())
        finally:
            print(sys.stderr, 'closing socket')
            sock.close()
            sendtoServer(r_packet.to_String()+" initiated from"+str(my_id))
    else:
        print("ER")
        split_ = r_packet.pathNow.split("-")
        i = 1
        loc = -1
        print("Len", split_)
        while i < len(split_):
            if split_[i] == str(my_id):
                loc = i - 1
                break
            i += 1
        print("Loc", loc)
        r_packet.packet_type="RRER"
#        sendRRep(r_packet, split_[loc], my_id)


def InitiateDataPacket(my_id,r_packet):
    path_split=r_packet.pathNow.split("-")
    to_send_id=int(path_split[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    port_no = 10000 + to_send_id
    server_address = ('localhost', port_no)
    print(sys.stderr, 'connecting to %s port %s' % server_address)
    sock.connect(server_address)
    try:
        # Send data

        packet=Packet("DATA",seq_no,r_packet.message,str(my_id),path_split[len(path_split)-1],0,0,str(my_id))
        packet.pathNow=r_packet.pathNow
        message = packet.to_String()


        print(sys.stderr, 'sending "%s"' % message)
        sock.send(message.encode())
    finally:
        print(sys.stderr, 'closing socket')
        sock.close()
        packet = Packet("DATA", seq_no, r_packet.message, str(my_id), path_split[len(path_split) - 1], 0, 0, str(my_id))
        packet.pathNow = r_packet.pathNow
        sendtoServer(packet.to_String()+",initiated from"+str(my_id))

def InitiateRREP(my_id,pathN,msg):          #(-5-0-2-4)len-1=4, len-2=2
    path_split=pathN.split("-")
    to_send_id=int(path_split[len(path_split)-2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    port_no = 10000 + to_send_id
    server_address = ('localhost', port_no)
    print(sys.stderr, 'connecting to %s port %s' % server_address)
    sock.connect(server_address)
    try:
        # Send data
        packet=Packet("RREP",0,msg,str(my_id),path_split[1],0,0,str(my_id))
        packet.pathNow=pathN
        message = packet.to_String()

        print(sys.stderr, 'sending "%s"' % message)
        sock.send(message.encode())
    finally:
        print(sys.stderr, 'closing socket')
        sock.close()
        packet = Packet("RREP", 0, msg, str(my_id), path_split[1], 0, 0, str(my_id))
        packet.pathNow = pathN
        sendtoServer(packet.to_String()+",initiated from "+str(my_id))

def sendRRep(recieved_packet,send_to,my_id):

    if findIfExists(my_id, int(send_to))==1:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        port_no = 10000 + int(send_to)

        server_address = ('localhost', port_no)
        print(sys.stderr, 'connecting to %s port %s' % server_address)
        sock.connect(server_address)
        try:
            # Send data
            recieved_packet.previous_node = str(my_id)
            #                input.pathNow+="-"+str(my_id)

            message = recieved_packet.to_String()
            print(sys.stderr, 'sending "%s"' % message)
            sock.send(message.encode())
        finally:
            print(sys.stderr, 'closing socket')
            sock.close()
    elif recieved_packet.packet_type=="DATA":
        #Generate ERR
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        port_no = 10000 + int(recieved_packet.previous_node)
        server_address = ('localhost', port_no)
        print(sys.stderr, 'connecting to %s port %s' % server_address)
        sock.connect(server_address)
        try:
            recieved_packet.previous_node = str(my_id)
            recieved_packet.packet_type="RERR"
            recieved_packet.message+="RERR"+str(my_id)+"-"+send_to
            message = recieved_packet.to_String()
            print(sys.stderr, 'sending "%s"' % message)
            sock.send(message.encode())
        finally:
            print(sys.stderr, 'closing socket')
            sock.close()


        print("eR")


def findIfExists(my_id,neighbor):
    print("Ln113")
    neighbors = list(G.neighbors(my_id))
    i=0
    while i<len(neighbors):
        if neighbor==neighbors[i]:
            print("Ln118")
            return 1
        i+=1
    print("Ln120")
    return 0
def sendtoServer(inp_string):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 9000)
    sock.connect(server_address)
    try:
        sock.send(inp_string.encode())
    finally:
        print(sys.stderr, 'closing socket')
        sock.close()

def sendPackets(input,nodes,my_id):
    id=my_id
    neighbors = list(G.neighbors(id))
    if input.previous_node!="":
        print("pn",int(input.previous_node))
        neighbors.remove(int(input.previous_node))
    sendInfo=str(my_id)+" is sending Packet (sender:"+input.sender+":destination:"+input.destination+":seq_no:"+str(input.sequence_number)+"prev_node"+input.previous_node+") to"
    neighborstr = ' '.join([str(elem) for elem in neighbors])
    sendInfo+=neighborstr
    sendtoServer(sendInfo)
    print("\nMy neighbors are ",neighbors,'\n')
    i=0
    input.pathNow += "-" + str(my_id)

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
#                input.pathNow+="-"+str(my_id)
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
    loc_x=0.0
    loc_y=0.0
    previous_node=""
    pathNow=""
    def __init__(self, packet_, id,message, sender,destination,loc_x,loc_y,prev):
        self.packet_type=packet_
        self.sequence_number=id
        self.message = message
        self.sender = sender
        self.destination=destination
        self.loc_x=loc_x
        self.loc_y=loc_y
        self.previous_node=prev
        self.pathNow=""
    def to_String(self):
        packet_string=self.packet_type+','+str(self.sequence_number)+','+self.message+','+self.sender+','+self.destination+','+str(self.loc_x)+','+str(self.loc_y)+','+self.previous_node+','+self.pathNow
        return packet_string


def to_Packet(packet_string):
    split_information = packet_string.split(',')
    rp= Packet(split_information[0],int(split_information[1]),split_information[2],split_information[3],split_information[4],split_information[5],split_information[6],split_information[7])
    rp.pathNow=split_information[8]
    return rp
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
    print("Sender", packet.sender," Destination",packet.destination," Previous Node:",packet.previous_node," Path",packet.pathNow,"\n")
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
            if findIfExists(my_id, int(dest)) == 0:
                if routeCheck(dest)=="-1":
                    packet=Packet("RREQ",seq_no,message,str(my_id),str(dest),str(loc_x),str(loc_y),"")
                    sendPackets(packet,nodes,my_id)
                    seq_no+=1
                else:
                    packet=Packet("DATA",seq_no,message,str(my_id),str(dest),str(loc_x),str(loc_y),"")
                    packet.pathNow=routeCheck(dest)
                    print_packet(packet)
                    sendDataPacket(my_id,packet)
            else:
                packet = Packet("DATA", seq_no, message, str(my_id), str(dest), str(loc_x), str(loc_y), "")

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Connect the socket to the port where the server is listening
                port_no = 10000 + int(dest)
                server_address = ('localhost', port_no)
                print(sys.stderr, 'connecting to %s port %s' % server_address)
                sock.connect(server_address)
                try:
                    # Send data
                    packet.previous_node = str(dest)
                    message = packet.to_String()
                    sendtoServer(packet.to_String() + " initiated from" + str(my_id))
                    print(sys.stderr, 'sending "%s"' % message)
                    sock.send(message.encode())
                finally:
                    print(sys.stderr, 'closing socket')
                    sock.close()






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
        amount_received = 0'
        amount_expected = len(message)
        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print(sys.stderr, 'received "%s"' % data)
    finally:
        print(sys.stderr, 'closing socket')
        sock.close()
"""


