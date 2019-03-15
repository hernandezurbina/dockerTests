import networkx as nx
from django.db import connection
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
#from ntgApp.urls import kwGraph
from ntgFrontend.tools import kwGraph

def showShortestPath(sourceNode, targetNode):
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
        fullPath += "{0} - {1} - ".format(path[i], kwGraph.get_edge_data(path[i], path[i+1])['id_publication'])

    fullPath += path[pathLen-1]
    return fullPath

@api_view(['GET'])
def knowledge_path(request):
    """
    API endpoint that returns the knowledge path between a pair of keywords
    """

    kw1 = request.GET.get('kw1', None)
    kw2 = request.GET.get('kw2', None)
    if kw1 is not None and kw2 is not None :
        print(request.query_params)
        results = showShortestPath(kw1, kw2)
        if results == 0:
            return Response("Either source or target node is not in KW graph", status=status.HTTP_400_BAD_REQUEST)
        else:
            if results == 1:
                return Response("No path between nodes", status=status.HTTP_400_BAD_REQUEST)
    else:
        print("No keyword in URL")
        return Response("Bad keyword in URL query", status=status.HTTP_400_BAD_REQUEST)

    return Response(results, status=status.HTTP_200_OK)

@api_view(['GET'])
def publications(request):
    """
    API endpoint that lists all publications
    """
    query = '''
    SELECT id_publication, title, publication_date
    FROM ntgBackend_publication
    ORDER BY RAND()
    LIMIT 100
    '''
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        descr = cursor.description
        rows = cursor.fetchall()
        results = [dict(zip([column[0] for column in descr], row)) for row in rows]

    finally:
        cursor.close()

    return Response(results, status=status.HTTP_200_OK)

@api_view(['GET'])
def publication_detail(request):
    """
    API endpoint that lists details of a single publication
    based on id_publication
    """
    query = '''
    SELECT id_publication, title, abstract, publication_date
    FROM ntgBackend_publication
    WHERE id_publication = {0}
    '''

    id_publication = request.GET.get('id_publication', None)
    if id_publication is not None:
        print(request.GET['id_publication'])
        print(request.query_params)
    else:
        print("No id in URL")
        results = "Bad id_publication in URL query"
        return Response(results, status=status.HTTP_400_BAD_REQUEST)

    try:
        cursor = connection.cursor()
        numRows = cursor.execute(query.format(id_publication))

        if numRows == 0:
            results = "No results with that ID"
            return Response(results, status=status.HTTP_204_NO_CONTENT)

        descr = cursor.description
        rows = cursor.fetchall()
        # results = [dict(zip([column[0] for column in descr], row)) for row in rows]
        # print("This worked!")

        # Below NEW logic to extract keyword, author and affiliation data
        # per publication:

        ### Main Loop
        results = []
        for row in rows:
            row2dict = dict(zip([column[0] for column in descr], row))

            id_publication = row[0]

            #Extract keywords
            queryKeywords = """
            SELECT a.keyword
            FROM ntgBackend_keyword a,
            ntgBackend_keyword_publication b,
            ntgBackend_publication c
            WHERE a.id_keyword = b.id_keyword_id
            AND b.id_publication_id = c.id_publication
            AND c.id_publication = {0}
            ORDER BY a.keyword
            """

            cursor.execute(queryKeywords.format(id_publication))
            kwRows = cursor.fetchall()
            row2dict["keywords"] = [kwRow[0] for kwRow in kwRows]

            #Extract authors
            queryAuthors = """
            SELECT a.id_author, a.author_name as author
            FROM ntgBackend_author a,
            ntgBackend_publication_author b,
            ntgBackend_publication c
            WHERE a.id_author = b.id_author_id
            AND b.id_publication_id = c.id_publication
            AND c.id_publication = {0}
            ORDER BY a.author_name
            """

            cursor.execute(queryAuthors.format(id_publication))
            authorRows = cursor.fetchall()
            row2dict["authors"] = []
            for authorRow in authorRows:
                dictAuthor = {}
                id_author = authorRow[0]
                dictAuthor["author_name"] = authorRow[1]

                queryAffiliations = """
                SELECT a.affiliation
                FROM ntgBackend_affiliation a,
                ntgBackend_publication_author_affiliation b,
                ntgBackend_publication_author c
                WHERE a.id_affiliation = b.id_affiliation_id
                AND b.id_publication_author_id = c.id_publication_author
                AND c.id_publication_id = {0}
                AND c.id_author_id = {1}
                ORDER BY a.affiliation
                """
                cursor.execute(queryAffiliations.format(id_publication, id_author))
                affRows = cursor.fetchall()
                dictAuthor["affiliations"] = [affRow[0] for affRow in affRows]
                row2dict["authors"].append(dictAuthor)

            results.append(row2dict)

    finally:
        cursor.close()

    return Response(results, status=status.HTTP_200_OK)
