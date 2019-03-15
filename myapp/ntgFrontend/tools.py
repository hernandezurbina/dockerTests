# from ntgApp.urls import kwGraph
# from ntgApp.urls import modelRF
# from ntgApp.urls import modelW2V
# from ntgApp.urls import clusterData

import networkx as nx
import numpy as np
import math

# WE'RE USING THE DEFAULT CACHE TYPE.
# IN PRODUCTION THIS CACHE TYPE MUST CHANGE.
from django.core.cache import cache

import pickle
from gensim.models import Word2Vec
import json
from sklearn.externals import joblib

# -----------------------------------------
# Load models and required files into cache
# -----------------------------------------

kwGraph_cache_key = 'kwGraph_cache'
kwGraph = cache.get(kwGraph_cache_key)

if kwGraph is None:
    print("kwGraph not found in cache. Loading kwGraph!")
    kwGraph = nx.read_gpickle("allKWs.gpickle") # This takes some time!
    #save in django memory cache
    cache.set(kwGraph_cache_key, kwGraph, None)
    print("kwGraph loaded!")
    print()

# Load KW graph into memory!
# print("Loading KW graph!")
# kwGraph = nx.read_gpickle("allKWs.gpickle") # This takes some time!
# print("KW graph loaded!")
# print()

modelRF_cache_key = 'modelRF_cache'
modelRF = cache.get(modelRF_cache_key)

if modelRF is None:
    print("RF model not found in cache. Loading RF model!")
    modelRF = joblib.load('modelRF.pkl')
    #save in django memory cache
    cache.set(modelRF_cache_key, modelRF, None)
    print("RF model loaded!")
    print()

# print("Loading RF model!")
# # with open('modelRF.pickle', 'rb') as f:
# #     modelRF = pickle.load(f)
# modelRF = joblib.load('modelRF.pkl')
# print("RF model loaded!")
# print()

modelSVC_cache_key = 'modelSVC_cache'
modelSVC = cache.get(modelSVC_cache_key)

if modelSVC is None:
    print("SVM model not found in cache. Loading SVM model!")
    modelSVC = joblib.load('modelSVC.pkl')
    #save in django memory cache
    cache.set(modelSVC_cache_key, modelSVC, None)
    print("SVM model loaded!")
    print()

# print("Loading SVM model!")
# # with open('modelSVC.pickle', 'rb') as f:
# #     modelSVC = pickle.load(f)
# modelSVC = joblib.load('modelSVC.pkl')
# print("SVM model loaded!")
# print()

modelW2V_cache_key = 'modelW2V_cache'
modelW2V = cache.get(modelW2V_cache_key)

if modelW2V is None:
    print("Word2Vec model not found in cache. Loading word2vec model!")
    modelW2V = Word2Vec.load("word2vec.model")
    #save in django memory cache
    cache.set(modelW2V_cache_key, modelW2V, None)
    print("Word2Vec model loaded!")
    print()
#
# print("Loading word2vec model!")
# modelW2V = Word2Vec.load("word2vec.model")
# print("Word2vec model loaded!")
# print()

clusterData_cache_key = 'clusterData_cache'
clusterData = cache.get(clusterData_cache_key)

if clusterData is None:
    print("ClusterData model not found in cache. Loading clusterData!")
    with open('kwDictArray.txt', 'r') as f:
        clusterData = json.load(f)
    #save in django memory cache
    cache.set(clusterData_cache_key, clusterData, None)
    print("clusterData loaded!")
    print()
# print("Loading cluster data!")
# with open('kwDictArray.txt', 'r') as f:
#     clusterData = json.load(f)
# print("Cluster data loaded!")
# print()

authorKWGraph_cache_key = 'authorKWGraph_cache'
authorKWGraph = cache.get(authorKWGraph_cache_key)

if authorKWGraph is None:
    print("authorKWGraph not found in cache. Loading authorKWGraph!")
    authorKWGraph = nx.read_gpickle("completeAuthorKWgraph.gpickle") # This takes some time!
    #save in django memory cache
    cache.set(authorKWGraph_cache_key, authorKWGraph, None)
    print("authorKWGraph loaded!")
    print()


def showShortestPathWithHREF(sourceNode, targetNode):
    try:
        path = nx.shortest_path(kwGraph,source=sourceNode,target=targetNode)
    except nx.NodeNotFound:
        #print("Either source or target node is not in KW graph")
        return 0
    except nx.NetworkXNoPath:
        #print("No path between nodes")
        return 1
    pathLen = len(path)
    fullPath = ""
    for i in range(pathLen - 1):
        idPubs = kwGraph.get_edge_data(path[i], path[i+1])['id_publication']
        fullPath += "{0} - ".format(path[i])
        for idPub in idPubs:
            fullPath += "<a href='pubDetails?idPub={0}'>[{0}]</a> ".format(idPub)
        fullPath += "- "
            #fullPath += "{0} - {1} - ".format(path[i], kwGraph.get_edge_data(path[i], path[i+1])['id_publication'])

    fullPath += path[pathLen-1]
    return fullPath


def CN(graph, node1, node2):
    return len(sorted(nx.common_neighbors(graph, node1, node2)))

def Salton(graph, node1, node2):
    try:
        salton = CN(graph, node1, node2) / math.sqrt(graph.degree(node1) * graph.degree(node2))
        return salton
    except ZeroDivisionError:
        return 0

def computeNeighborSimilarity(G, kw1, kw2):
    '''
    this function estimates the similarity between kw1 and kw2's neighbors
    and returns mean and std dev
    the function receives graph G as parameter to obtain neighbors of kw2
    kw1 and kw2 will be given with underscores replacing spaces
    '''
    meanSim = 0
    stdSim = 0
    node1 = kw1.replace('_', ' ')
    node2 = kw2.replace('_', ' ')
    # get all neighbors from node2
    if G.degree(node2) > 0:
        sims = []
        for node3 in G.neighbors(node2):
            # if node3 (neighbor of node2) isn't the same as node1, estimate similarity between node1 and node3
            if node3 != node1:
                kw3 = node3.replace(' ', '_')
                # accumulate the result in sumTotal
                sims.append(computeSim(kw1, kw3))
        # once all neighbors have been processed, divide sumTotal by the degree of node2, ie. obtain average
        # afterwards compute the variance
        meanSim = np.mean(sims)
        stdSim = np.std(sims)

    return meanSim, stdSim

def computeSim(kw1, kw2):
    try:
        sim = modelW2V.wv.similarity(kw1, kw2)
        if sim < 0:
            sim = 0
    except KeyError:
        #print("One of the KWs is not in the vocab")
        sim = 0
    #print(sim)
    return sim

def retrieveClusters(idKw):
    for i in range(len(clusterData)):
        if idKw == clusterData[i]['id_keyword']:
            return clusterData[i]['clusters']
    return []

def addFeatures(graph, node1, node2):
    data = np.zeros(25, dtype='float32')

    idkw1 = graph.node[node1]['id_keyword']
    idkw2 = graph.node[node2]['id_keyword']

    # underscored KW is required for w2v model
    # not underscored KW is required for network operations
    kw1 = node1.replace(' ', '_')
    kw2 = node2.replace(' ', '_')

    data[0] = Salton(graph, node1, node2)
    data[1] = computeSim(kw1, kw2)
    data[2] = nx.clustering(graph, node1)
    data[3] = nx.clustering(graph, node2)
    data[4], data[5] = computeNeighborSimilarity(graph, node1, node2)
    data[6], data[7] = computeNeighborSimilarity(graph, node2, node1)

    kw1Clusters = retrieveClusters(idkw1)
    kw2Clusters = retrieveClusters(idkw2)

    data[8] = 1 if 0 in kw1Clusters else 0
    data[9] = 1 if 1 in kw1Clusters else 0
    data[10] = 1 if 2 in kw1Clusters else 0
    data[11] = 1 if 3 in kw1Clusters else 0
    data[12] = 1 if 4 in kw1Clusters else 0
    data[13] = 1 if 5 in kw1Clusters else 0
    data[14] = 1 if 6 in kw1Clusters else 0
    data[15] = 1 if 7 in kw1Clusters else 0

    data[16] = 1 if 0 in kw2Clusters else 0
    data[17] = 1 if 1 in kw2Clusters else 0
    data[18] = 1 if 2 in kw2Clusters else 0
    data[19] = 1 if 3 in kw2Clusters else 0
    data[20] = 1 if 4 in kw2Clusters else 0
    data[21] = 1 if 5 in kw2Clusters else 0
    data[22] = 1 if 6 in kw2Clusters else 0
    data[23] = 1 if 7 in kw2Clusters else 0

    # label
    data[24] = 1 if graph.get_edge_data(node1,node2) else 0

    return data

def probOfConnectivity(node1, node2):
    data = addFeatures(kwGraph, node1, node2)
    outputRF = modelRF.predict_proba([data[0:24]])
    outputSVC = modelSVC.predict_proba([data[0:24]])
    probRF = outputRF[0][1]
    probSVC = outputSVC[0][1]
    return probRF, probSVC


def kwRecommendationM1(author):
    """
    author is as extracted from the DB (e.g. A Block)
    """
    suggestedKWs = []
    idAuthorInG = [x for x,y in authorKWGraph.nodes(data=True) if y['value']==author]
    idAuthorInG = idAuthorInG[0]
    # list all neighbors of author
    coauthors = []
    authorKWs = []
    for node in authorKWGraph.neighbors(idAuthorInG):
        if authorKWGraph.node[node]['table'] == 'keywords':
            #authorKWs.append(node)
            kw = authorKWGraph.node[node]['value']
            authorKWs.append(kw)
        else:
            if authorKWGraph.node[node]['table'] == 'authors':
                coauthors.append(node)
    # for each coauthor do:
    for coauthor in coauthors:
        for node in authorKWGraph.neighbors(coauthor):
            #if (G.node[node]['table'] == 'keywords') and (node not in authorKWs) and (node not in suggestedKWs):
            if (authorKWGraph.node[node]['table'] == 'keywords'):
                kw = authorKWGraph.node[node]['value']
                if (kw not in authorKWs) and (kw not in suggestedKWs):
                    suggestedKWs.append(kw)
    return suggestedKWs

def kwRecommendationM2(author):
    """
    author is as extracted from the DB (e.g. A Block)
    requires authorKWGraph in memory
    """
    suggestedKWs = []
    idAuthorInG = [x for x,y in authorKWGraph.nodes(data=True) if y['value']==author]
    idAuthorInG = idAuthorInG[0]
    authorCluster = authorKWGraph.node[idAuthorInG]['cluster']

    # obtain authors in same cluster as current author
    coClusterees = [x for x,y in authorKWGraph.nodes(data=True) if y['table']=='authors' and y['cluster']== authorCluster]

    # obtain KWs of current author
    authorKWs = []
    for node in authorKWGraph.neighbors(idAuthorInG):
        if authorKWGraph.node[node]['table'] == 'keywords':
            authorKWs.append(node)

    # for each author in cluster
    for coauthor in coClusterees:
        for node in authorKWGraph.neighbors(coauthor):
            if (authorKWGraph.node[node]['table'] == 'keywords') and (node not in authorKWs) and (node not in suggestedKWs):
                suggestedKWs.append(node)

    return suggestedKWs
