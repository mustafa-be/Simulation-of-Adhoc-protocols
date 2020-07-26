import pickle
from networkx.generators.random_graphs import erdos_renyi_graph
import networkx as nx
import matplotlib.pyplot as plt
def generate_connected_graph(nds,p):
    n = nds
    i = 0
    while(1):
        G = erdos_renyi_graph(n, p)
        # print("Iterator: ",i)
        # print(G.nodes)
        # print(G.edges)
        # print(nx.is_connected(G)) #return true if all nodes in geaph connected
        # nx.draw_networkx(G)
        # plt.show()
        if(nx.is_connected(G)):
            break;
        i = i + 1
        # print('\n------------------------\n')
    return G


n = 50
p = 0.4
#G = erdos_renyi_graph(n, p)
G = generate_connected_graph(n,0.2)
print(list(G.edges))
#pos = nx.spring_layout(G)
#nx.draw_networkx(G, pos)
#plt.show()
f = open('store.pckl', 'wb')
pickle.dump(G, f)
f.close()

