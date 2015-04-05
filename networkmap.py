import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import string

G = nx.generators.erdos_renyi_graph(18, 0.2)
nx.draw(G,
        node_color = np.linspace(0,1,len(G.nodes())),
        edge_color = np.linspace(0,1,len(G.edges())),
        width = 3.0,
        labels = {n:l for n,l in zip(G.nodes(),string.ascii_uppercase)}
        )
plt.savefig('graph.png')

plt.show()
