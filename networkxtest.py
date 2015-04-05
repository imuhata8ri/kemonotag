#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import codecs
stdin = sys.stdin
#sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
sys.stdin  = codecs.getreader('euc_jp')(sys.stdin)
sys.stdout = codecs.getwriter('shift_jis')(sys.stdout)
sys.path.insert(0,'lib')
reload(sys)
sys.setdefaultencoding('utf-8')
#sys.stdout = stdout
#sys.path.append(os.pardir)
sys.path.append(os.pardir + '/lib/')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import math

import StringIO
import numpy
import matplotlib.pyplot as plt
import networkx as nx

import numpy as np

#-------------------------Define Edges-------------------------
allLines = open('edges3.csv').read().encode('utf-8')

data = StringIO.StringIO(allLines)
G = nx.Graph()

#edges = nx.read_edgelist(data, delimiter=',', nodetype=unicode, create_using=nx.DiGraph())
edges = nx.read_edgelist(data, delimiter=',', nodetype=unicode)

N,K = edges.order(), edges.size()
avg_deg = float(K)/N
print "Nodes: ", N
print "Edges: ", K
print "Average degree: ", avg_deg

for e in edges.edges():
    G.add_edge(*e)


#'Fan-boy' trimmer
def remove_edges(g, in_degree=1, out_degree=1):
    g2=g.copy()
    #d_in=g2.in_degree(g2)
    #d_out=g2.out_degree(g2)
    #print(d_in)
    #print(d_out)
    d = g2.degree(g2)
    #print d
    for n in g2.nodes():
        #if d_in[n]==in_degree and d_out[n] == out_degree: 
        if d[n]==in_degree:
            g2.remove_node(n)
    return g2

#G_trimmed = remove_edges(G)
G = remove_edges(G)
#G_trimmed.edges()
##outputs [('C', 'G'), ('G', 'H'), ('K', 'J'), ('J', 'L')]
#G_trimmed.nodes()
##outputs ['A', 'C', 'G', 'F', 'H', 'K', 'J', 'L']


#-------------------------Finding Centrality-------------------------
cent = nx.closeness_centrality(G)
bet = nx.betweenness_centrality(G)
eig = nx.eigenvector_centrality(G)

def highest_centrality(cent_dict): 
    """Returns a tuple (node,value) with the node 
    with largest value from Networkx centrality dictionary.""" 
    # Create ordered tuple of centrality data
    cent_items=[(b,a) for (a,b) in cent_dict.iteritems()]
    # Sort in descending order 
    cent_items.sort() 
    cent_items.reverse() 
    return tuple(reversed(cent_items[0]))



pos=nx.get_edge_attributes(G,'pos')
plt.figure(figsize=(8,8))
'''
nx.draw_networkx_edges(G,pos,nodelist=[ncenter],alpha=0.4)
nx.draw_networkx_nodes(G,pos,nodelist=p.keys(),
                       node_size=80,
                       node_color=p.values(),
                       cmap=plt.cm.Reds_r)
'''

#nx.draw_networkx_nodes(G, pos, node_size = 100, node_color = 'w')
#nx.draw_networkx_edges(G, pos, width = 1)
#nx.draw_networkx_labels(G, pos, font_size = 12, font_family = 'sans-serif', font_color = 'r')
#nx.draw_networkx(G)


def most_important(G):
 """ returns a copy of G with
     the most important nodes
     according to the pagerank """ 
 ranking = nx.betweenness_centrality(G).items()
 #print ranking
 r = [x[1] for x in ranking]
 m = sum(r)/len(r) # mean centrality
 t = m*3 # threshold, we keep only the nodes with 3 times the mean
 Gt = G.copy()
 for k, v in ranking:
  if v < t:
   Gt.remove_node(k)
 return Gt

Gt = most_important(G) # trimming


def clustering(G):
    '''find cluster'''
    clustering = list(nx.clustering(G).items())
    #clustering = list(clustering.items())
    r = [x[1] for x in clustering]
    Gc = G.copy()
    for k, v in clustering:
        if v == 0:
            Gc.remove_node(k)
    return Gc





#--------------------------------------------------
import community
Gc = community.best_partition(G)
#Gc = nx.clustering(G)
#print "clustering",Gc
for n, m in Gc.items():
    Gc[n] = int(m)
color = []

for nodes in nx.nodes_iter(G):
    value = int(Gc[nodes]*100)
    color.append(value)
#print "color: ",color
nx.set_node_attributes(G,'group',Gc)

#--------------------------------------------------
'''
import community
#first compute the best partition
partition = community.best_partition(G)
import random
#drawing
size = float(len(set(partition.values())))
pos = nx.spring_layout(G)
count = 0.
for com in set(partition.values()) :
    count = count + 1.
    list_nodes = [nodes for nodes in partition.keys()
                                if partition[nodes] == com]
    nx.draw_networkx_nodes(G, pos, list_nodes, node_size = 20,
                                np.linspace(0,1,len(G.nodes())))
                                #str(random.random()*(count / size)))
                                #node_color = str(count / size))

nx.draw_networkx_edges(G,pos, alpha=0.2)
'''

#clustering = nx.clustering(G)
#print clustering


#bb=nx.eigenvector_centrality(G)
#nx.set_node_attributes(G,'betweenness',bb)
#bb.update((x, int(y*1000)+1) for x, y in bb.items())

#bb=nx.betweenness_centrality(G)
#nx.set_node_attributes(G,'betweenness',bb)


#--------------------------------------------------
#大きさを定義するリストを作成
#bb=nx.degree_centrality(G)
#bb=nx.betweenness_centrality(G)
#bb=nx.closeness_centrality(G)
bb=nx.eigenvector_centrality(G)
for n, m in bb.items():
    bb[n] = int(math.ceil(m*25))
    #print bb[n]

test = []
for nodes in nx.nodes_iter(G):
    value = int(bb[nodes]*100)
    #print value
    test.append(value)
#print len(test)
#print bb
#for n in len(test):
    #nx.set_node_attributes(G, 'betweenness',
nx.set_node_attributes(G,'betweenness',bb)
#--------------------------------------------------

#print test
#print nodes.encode(sys.stdout.encoding, errors='replace')


#bb.update((x, int(y*1000)+1) for x, y in bb.items())

#bb = nx.current_flow_betweenness_centrality(G)
#nx.set_node_attributes(G,'betweenness',bb)
#bb.update((x, int(y*10)+1) for x, y in bb.items())

#print bb
#test = bb.values()

import numpy as np
test = np.asarray(test)
#print nx.number_of_nodes(G)
#print test

#for nodes in nx.nodes_iter(G):
    #print nodes.encode(sys.stdout.encoding, errors='replace')


#print type(bb)
#for n in G.nodes_iter():
    #ss = int(G.node[n]['betweenness']*1000)
    #print type(ss)
    #nx.set_node_attributes(G,'size',ss)

#for nodes in nx.nodes_iter(G):
    #print nodes.encode(sys.stdout.encoding, errors='replace')

from pylab import show
# create the layout
pos = nx.spring_layout(G)

# draw the nodes and the edges (all)
#for nodes in G:
    #print nodes
#print G.node[1]['betweenness']
#for n in G.nodes_iter():
#    print int(G.node[n]['betweenness']*1000)
nx.draw_networkx_nodes(G,pos,node_color=color,alpha=0.8,node_size=test)
#nx.draw_networkx_nodes(G,pos,node_color='b',alpha=0.8,node_size=1)
nx.draw_networkx_edges(G,pos,alpha=0.2)
nx.draw_networkx_labels(G,pos,font_size=10,font_color='black')
# draw the most important nodes with a different style
#nx.draw_networkx_nodes(Gt,pos,node_color='r',alpha=0.8)
#nx.draw_networkx_nodes(Gt,pos,node_size='bb')
#values = [val_map.get(node, 0.25) for node in Gc.nodes()]
#for n in Gc:
#    print(Gc[n])
#nx.draw_networkx_nodes(Gc,pos,node_color=node[1])
# also the labels this time
#nx.draw_networkx_labels(Gt,pos,font_size=12,font_color='black')
#show()
#plt.savefig('graph_test.png')

import json as json
# add nodes, edges, etc to G ...

def save(G, fname):
    from networkx.readwrite import json_graph
    data = json_graph.dumps(G, sort_keys=True,indent=2)
    f = open(fname, 'w')
    #json.dump(data, f)
    f.write(data)
    #json.dump(dict(nodes=[[n, G.node[n]] for n in G.nodes()],
                   #edges=[[u, v, G.edge[u][v]] for u,v in G.edges()]),
              #open(fname, 'w'), indent=2)

#nx.draw_spring(G)
save(G, "./d3/graph.json")
plt.savefig('./d3/graph_test.png')
#plt.show()



# ('1', '3')
# ('1', '2')
# ('3', '2')
