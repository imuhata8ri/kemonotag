!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import codecs
stdin = sys.stdin
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
sys.stdin  = codecs.getreader('euc_jp')(sys.stdin)
sys.path.insert(0,'lib')
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.pardir + '/lib/')

import StringIO
import networkx as nx
import matplotlib.pyplot as plt
from pylab import show
import math
import json as json

def createjson(datas):
    #-------------------------Define Edges-------------------------:
    
    #allLines = open('edges5.Csv').read().encode('utf-8')
    allLines = datas.encode('utf-8')
    #allLines = open(/csv).read().encode('utf-8')
    
    data = StringIO.StringIO(allLines)
    G = nx.Graph()
    edges = nx.read_edgelist(data, delimiter=',', nodetype=unicode)
    
    for e in edges.edges():
        G.add_edge(*e)
    
    #-------------------------Calculate statistics-------------------------
    N,K = edges.order(), edges.size()
    print "Nodes: ", N
    print "Edges: ", K
    
    avg_deg = int(math.ceil(float(K)/N))
    print "Average degree: ", avg_deg
    
    degree = G.degree()
    degreelist = []
    for n in degree:
        degreelist.append(degree[n])
    degreelist = filter(lambda x: x>1, degreelist)
    
    #set min %
    degreelist.sort()
    topp = 90
    topn = 50
    toplist = degreelist[int(len(degreelist) * topp/100) : int(len(degreelist))]
    median=sorted(degreelist)[len(degreelist)/2]
    mediantopp=sorted(toplist)[len(toplist)/2]
    print "Degree Median: ", median
    print "Degree Median(top %): ", mediantopp
    
    Range = (max(degreelist)-min(degreelist))
    Rangetopp = (max(toplist)-min(toplist))
    
    print "Degree Range: ", Range
    print "Degree Range(top %): ", Rangetopp
    
    
    #-------------------------Trim down tagalongs-------------------------
    #'Fan-boy' trimmer
    def remove_edges(g, in_degree):
        g2=g.copy()
        #d_in=g2.in_degree(g2)
        #d_out=g2.out_degree(g2)
        d = g2.degree(g2)
        for n in g2.nodes():
            #if d_in[n]==in_degree and d_out[n] == out_degree: 
            if d[n] <= in_degree:
                g2.remove_node(n)
        return g2
    
    def remove_minoredges(g, topn):
        import heapq
        g3=g.copy()
        d = g3.degree(g3)
        #d.most_common()
        a = sorted(d, key=d.get, reverse=False)[:int(len(d)-topn)]
        for item in a:
            g3.remove_node(item)
        return g3
    
    
    #G = remove_edges(G,mediantopp)
    G = remove_minoredges(G,topn)
    
    #-------------------------Finding Community-------------------------
    import community
    Gc = community.best_partition(G)
    for n, m in Gc.items():
        Gc[n] = int(m)
    
    color = []
    for nodes in nx.nodes_iter(G):
        value = int(Gc[nodes]*100)
        color.append(value)
    nx.set_node_attributes(G,'group',Gc)
    #-------------------------Finding Centrality-------------------------
    #大きさを定義するリストを作成
    #bb=nx.degree_centrality(G)
    #bb=nx.betweenness_centrality(G)
    #bb=nx.closeness_centrality(G)
    bb=nx.eigenvector_centrality(G)
    for n, m in bb.items():
        bb[n] = int(math.ceil(m*25))
    
    size = []
    for nodes in nx.nodes_iter(G):
        value = int(bb[nodes]*100)
        size.append(value)
    nx.set_node_attributes(G,'betweenness',bb)
    #-------------------------Finding edge Centrality-------------------------
    #線分の大きさを定義するリストを作成
    cc=nx.edge_betweenness_centrality(G)
    for n, m in cc.items():
        cc[n] = int(math.ceil(m*500))
    
    edgesize = []
    for edges in nx.edges_iter(G):
        value = int(cc[edges]*500)
        edgesize.append(value)
    nx.set_edge_attributes(G,'length',cc)
    #--------------------------------------------------
    G = remove_minoredges(G,topn)
    
    from networkx.readwrite import json_graph
    data = json_graph.dumps(G, sort_keys=True,indent=2)
    
    return data
    
    #def save(G, fname):
    #    from networkx.readwrite import json_graph
    #    data = json_graph.dumps(G, sort_keys=True,indent=2)
    #    f = open(fname, 'w')
    #    f.write(data)
    
    #save(G, "./d3/graph.json")
    
