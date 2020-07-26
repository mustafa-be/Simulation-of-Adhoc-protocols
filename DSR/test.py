import random
from random import randint
import networkx as nx
import pickle
import matplotlib.pyplot as plt

f = open('store.pckl', 'rb')
G = pickle.load(f)
f.close()

pos = nx.spring_layout(G)
nx.draw_networkx(G, pos)
plt.show()

nodes=50
value = randint(1, 15)
if value>7:
    value=randint(1,15)

print("Change ",value/100.0,"% Nodes")

no_of_nodes_changed=(value/100.0)*nodes
print("B",no_of_nodes_changed)
if(no_of_nodes_changed<0):
    no_of_nodes_changed=1
print("A:No of nodes to change=",no_of_nodes_changed)
if no_of_nodes_changed<1:
    no_of_nodes_changed=1
nodes_to_change=random.sample(list(G.nodes), int(no_of_nodes_changed))
print("Nodes chosen whose edges are going to change",nodes_to_change)
i=0
edges = list(G.edges)
non_edges=list(nx.non_edges(G))
while i<len(nodes_to_change):
    n_edges=[x for x in edges if nodes_to_change[i] == x[0] or nodes_to_change[i]==x[1]]
    print("Edges of ",nodes_to_change[i]," are ", n_edges)
    n_non_edges=[x for x in non_edges if nodes_to_change[i] == x[0] or nodes_to_change[i]==x[1]]
    print("Non edges of ",nodes_to_change[i], " are ",n_non_edges)
    if len(n_edges)>2:

        n_edges_delete=0.4*len(n_edges)
        print("No of Delete edges ",n_edges_delete)
        edges_to_del=random.sample(n_edges,int(n_edges_delete))
        print("Delete edges ",edges_to_del)
        for x in edges_to_del:
            G.remove_edge(x[0],x[1])

        n_edges_add = n_edges_delete
        print("No of edges to add",n_edges_add)
        edges_to_add = random.sample(n_non_edges, int(n_edges_add))
        print("Add edges ",edges_to_add)
        for x in edges_to_add:
            G.add_edge(x[0], x[1])
    else:
        print("Len<2, Simple adding an edge")
        chosen_edge = random.choice(n_non_edges)
        print("Adding to graph", chosen_edge)
        G.add_edge(chosen_edge[0], chosen_edge[1])
    i+=1

#g = G
#G.add_edge(2, 6)

#f = open('store.pckl', 'wb')
#pickle.dump(G, f)
#f.close()

if False:
    edges = list(g.edges)
    nonedges = list(nx.non_edges(g))
    # random edge choice
    print((edges),(nonedges))
    chosen_edge = random.choice(edges)
    print(chosen_edge)
    chosen_nonedge=[]
    #        if len([x for x in nonedges if chosen_edge[0] == x[0]])>0:
    print([x for x in nonedges if chosen_edge[0] == x[0] or chosen_edge[0]==x[1]])
    chosen_nonedge = random.choice([x for x in nonedges if chosen_edge[0] == x[0]])
    print()
    if True:
        # delete chosen edge
        g.remove_edge(chosen_edge[0], chosen_edge[1])
        print(chosen_edge[0],chosen_edge[1])
        # add new edge
        print("K",chosen_nonedge[0], chosen_nonedge[1],";")
        g.add_edge(chosen_nonedge[0], chosen_nonedge[1])
        print("Chosing: ",chosen_nonedge[0]," ",chosen_nonedge[1])
        if(nx.is_connected(g)):
            print("1")