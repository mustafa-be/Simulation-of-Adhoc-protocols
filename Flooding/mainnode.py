import sys
import socket
import _thread
import os
import time
import random
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from networkx.generators.random_graphs import erdos_renyi_graph
import networkx as nx
import pickle

nodes = 10
f = open('store.pckl', 'rb')
G = pickle.load(f)
f.close()

grid_row = np.zeros(nodes) 
grid_col = np.zeros(nodes)


def list_of_neighbors(row, col, node_number ,radius): #calculate list of neighbors from radius
    i = 0
    neighbors = [] #list of neighbors lie in the radius
    while(i < row.shape[0]):
        if(i != node_number):
            dist = np.sqrt((row[node_number]-row[i])**2 + (col[node_number]-col[i])**2)
            #print("Distance from ",node_number," to",i," : ",dist)
            if(dist <= radius):
                neighbors.append(i)
        i = i +1
    return neighbors

def delete_random_edge(graph, del_orig=True): #deletes a edge
    '''
    Create a new random edge and delete one of its current edge if del_orig is True.
    :param graph: networkx graph
    :param del_orig: bool
    :return: networkx graph
    '''
    edges = list(graph.edges)
    nonedges = list(nx.non_edges(graph))

    # random edge choice
    chosen_edge = random.choice(edges)
    chosen_nonedge = random.choice([x for x in nonedges if chosen_edge[0] == x[0]])

    if del_orig:
        # delete chosen edge
        graph.remove_edge(chosen_edge[0], chosen_edge[1])
    # add new edge
    #graph.add_edge(chosen_nonedge[0], chosen_nonedge[1])

    return graph


def server(mysocket,nodes):
    mysocket.listen(20)
    i=0
    while True:
        # Wait for a connection
        (connection, client_address) = mysocket.accept()
        try:
            # Receive the data in small chunks and retransmit it
            data = connection.recv(300)
#            print(sys.stderr, 'received "%s"' % data)
            print(str(data))

        finally:
            # Clean up the connection
            #print("sdas")
            print()

def startprocesses(threadname,nodes):
    time.sleep(2)
    print(threadname)
    gridsize = 0
    i = 1
    while i < nodes:
        gridsize += 1
        i = gridsize * gridsize
    print('Grid size:',gridsize)
#    i = 0
    i=0
    while (i < nodes):
        locx = random.uniform(0,gridsize - 1)                           #Irrelevant
        locx = float("{:.1f}".format(locx))
        grid_row[i] = locx          #saving random value on graph x
        
        locy = random.uniform(0,gridsize - 1)
        locy = float("{:.1f}".format(locy))
        grid_col[i] = locy          #saving random value on graph y    #Irrelevant
        
        cmd = "start /wait python nodes.py "
        returned_value = os.popen(cmd+str(i)+" "+str(locx)+" "+str(locy)+" "+str(nodes))    # opens terminal , runs nodes
        i = i + 1
    #Graph
    n = nodes
    p = 0.4
    f = open('store.pckl', 'rb')
    G = pickle.load(f)
    f.close()                   #Read graph from .pckl
#    G = erdos_renyi_graph(n, p)
#    print(list(G.edges))

    #print(list(G.neighbors(3))) gives list of neighbors
    #G.remove_node(1) delete node
    #new_G = delete_random_edge(G, del_orig=True) delete a random edge
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos)            #Show the graph
    plt.show()
    
#    f = open('store.pckl', 'wb')
#    pickle.dump(G, f)
#    f.close()
    
    #plot graph points
    # print('Row: ',grid_row,'\n')
    # print('Col: ',grid_col,'\n')
    # neighbors = list_of_neighbors(grid_row, grid_col, 0, 1.5)
    # print("Neighbors: ",neighbors)
    # plt.plot([grid_row], [grid_col], marker='o', markersize=3, color="red")
    # plt.show()
        


mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 9000)
print(sys.stderr, 'starting up on %s port %s' % server_address)     #Socket listening at 9000
mysocket.bind(server_address)

try:
    _thread.start_new_thread(server, (mysocket,nodes,))         # Server listen on port 9000
    _thread.start_new_thread(startprocesses,("Thread-1",nodes,))    # Starts  nodes processes
    while True:
        print("Input 1 to change topology\nEnter Dest")
        dest = input()
        if dest=="1":
            value = randint(1, 15)
            if value > 7:
                value = randint(1, 15)

            print("Change ", value / 100.0, "% Nodes")

            no_of_nodes_changed = (value / 100.0) * nodes
            print("B", no_of_nodes_changed)
            if (no_of_nodes_changed < 0):
                no_of_nodes_changed = 1
            print("A:No of nodes to change=", no_of_nodes_changed)
            if no_of_nodes_changed < 1:
                no_of_nodes_changed = 1
            nodes_to_change = random.sample(list(G.nodes), int(no_of_nodes_changed))  # [3.4.5.1]

            ## [0,1,2,3,4,5]  random.sample(list,2) ,,, 3,1
            print("Nodes chosen whose edges are going to change", nodes_to_change)
            i = 0
            edges = list(G.edges)  # [(1,2)(3,4)]
            non_edges = list(nx.non_edges(G))
            while i < len(nodes_to_change):
                n_edges = [x for x in edges if nodes_to_change[i] == x[0] or nodes_to_change[i] == x[1]]
                print("Edges of ", nodes_to_change[i], " are ", n_edges)
                n_non_edges = [x for x in non_edges if nodes_to_change[i] == x[0] or nodes_to_change[i] == x[1]]
                print("Non edges of ", nodes_to_change[i], " are ", n_non_edges)
                if len(n_edges) > 2:
                    n_edges_delete = 0.4 * len(n_edges)
                    print("No of Delete edges ", n_edges_delete)
                    edges_to_del = random.sample(n_edges, int(n_edges_delete))
                    print("Delete edges ", edges_to_del)
                    for x in edges_to_del:
                        G.remove_edge(x[0], x[1])

                    n_edges_add = n_edges_delete
                    print("No of edges to add", n_edges_add)
                    edges_to_add = random.sample(n_non_edges, int(n_edges_add))
                    print("Add edges ", edges_to_add)  # [(1,2)(3,1)]
                    for x in edges_to_add:
                        G.add_edge(x[0], x[1])
                else:
                    print("Len<2, Simple adding an edge")
                    chosen_edge = random.choice(n_non_edges)
                    print("Adding to graph", chosen_edge)
                    G.add_edge(chosen_edge[0], chosen_edge[1])
                i += 1
            # G.remove_edge(2,6)

            # G=change_neighbor(G,del_orig=True)
            # print("GGGEEE")
            # G = change_neighbor(G, del_orig=True)

            f = open('store.pckl', 'wb')
            pickle.dump(G, f)
            f.close()
            i = 0
            print("Changeeed")
            j = 0
            while j < nodes:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = ('localhost', 10000 + j)
                sock.connect(server_address)
                try:
                    sock.send("G-C".encode())
                finally:
                    print(sys.stderr, 'closing socket')
                    sock.close()
                j += 1

finally:
   print("Error: unable to start thread")


while 1:
    pass