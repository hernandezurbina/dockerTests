from .gen_json import generateGraph, generateStarGraph, generateChart
from django.shortcuts import render
from ntgFrontend.forms import KeywordForm, mainSearchForm
from django.db import connection
from ntgFrontend.validations import validateString, validateNumber


# There are a few functions that have been commented below
# along with the import clauses below in order to move everything
# to my computer and make it run from docker

# from ntgFrontend.tools import showShortestPathWithHREF
# from ntgFrontend.tools import probOfConnectivity
# from ntgFrontend.tools import kwRecommendationM1


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def pubDetails(request):
    if request.method == 'GET':
        if not request.GET.get('idPub'):
            return render(request, 'index.html')
        else:
            id_publication = validateNumber(request.GET.get('idPub'))
            context = {}

            # 1) Obtain publication details
            query = """
            SELECT title, abstract, publication_date, other_id AS cosyne_id
            FROM ntgBackend_publication
            WHERE id_publication = {0}
            """.format(id_publication)

            print(query)

            with connection.cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()

            context.update({"publicationDetails": row})

            # 2) Obtain authors
            query = """
            SELECT a.id_author, a.author_name
            FROM ntgBackend_author a
            INNER JOIN ntgBackend_publication_author b ON a.id_author = b.id_author_id
            INNER JOIN ntgBackend_publication c ON c.id_publication = b.id_publication_id
            AND c.id_publication = {0}
            ORDER BY a.author_name
            """.format(id_publication)

            print(query)

            with connection.cursor() as cursor:
                cursor.execute(query)
                rowsAuthor = cursor.fetchall()

            # context.update({"authorDetails": rowsAuthor})

            authorAffiliations = {}

            for author in rowsAuthor:
                authorAffiliations.update({author[1]: []})
                query = """
                SELECT a.affiliation
                FROM ntgBackend_affiliation a
                INNER JOIN ntgBackend_publication_author_affiliation b ON a.id_affiliation = b.id_affiliation_id
                INNER JOIN ntgBackend_publication_author c ON b.id_publication_author_id = c.id_publication_author
                INNER JOIN ntgBackend_author d ON c.id_author_id = d.id_author
                AND d.id_author = {0}
                GROUP BY a.affiliation
                ORDER BY a.affiliation
                """.format(author[0])
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    rowsAffiliations = cursor.fetchall()
                for affiliation in rowsAffiliations:
                    authorAffiliations[author[1]].append(affiliation[0])

            print(authorAffiliations)

            context.update({"authorAffiliations": authorAffiliations})
            # 3) Obtain affiliations

            # 4) Obtain KWs

            query = """
            SELECT a.keyword
            FROM ntgBackend_keyword a
            INNER JOIN ntgBackend_keyword_publication b ON a.id_keyword = b.id_keyword_id
            INNER JOIN ntgBackend_publication c ON c.id_publication = b.id_publication_id
            AND c.id_publication = {0}
            ORDER BY a.keyword
            """.format(id_publication)

            print(query)

            with connection.cursor() as cursor:
                cursor.execute(query)
                rowsKWs = cursor.fetchall()

            context.update({"keywords": rowsKWs})

            # Return all details to template
            context.update({"id_publication": id_publication})
            return render(request, 'pubDetails.html', context)
    else:
        return render(request, 'index.html')

# def keyword_path(request):
#     query = "SELECT id_keyword, keyword FROM ntgBackend_keyword ORDER BY keyword"
#     with connection.cursor() as cursor:
#         cursor.execute(query)
#         keywords = dictfetchall(cursor)
#     context = {"keywords": keywords}
#     #print(query)
#     if request.method == "POST":
#         keyword1 = request.POST.get('keyword1', None)
#         keyword2 = request.POST.get('keyword2', None)
#         context.update({"keyword1": keyword1})
#         context.update({"keyword2": keyword2})
#         errors = []
#
#         if keyword1 is not None and keyword2 is not None:
#             print(keyword1)
#             print(keyword2)
#             ##
#             path = showShortestPathWithHREF(keyword1, keyword2)
#
#             if path == 0:
#                 errors.append("Path estimation: Either source or target node is not in KW graph")
#             else:
#                 if path == 1:
#                     errors.append("No path between nodes")
#             ##
#             probRF, probSVC = probOfConnectivity(keyword1, keyword2)
#             if probRF == -1 or probSVC == -1:
#                 errors.append("Prob estimation: Either source or target node is not in KW graph")
#
#
#             if not errors:
#                 context.update({"path": path})
#                 probRF = probRF * 100
#                 probSVC = probSVC * 100
#                 context.update({"probRF": probRF})
#                 context.update({"probSVC": probSVC})
#                 print(probRF, probSVC)
#             else:
#                 context.update({"errors": errors})
#
#
#     return render(request, 'keyword_path.html', context)

# def keyword_recommendations(request):
#     query = "SELECT id_author, author_name FROM ntgBackend_author ORDER BY author_name"
#     with connection.cursor() as cursor:
#         cursor.execute(query)
#         authors = dictfetchall(cursor)
#     context = {"authors": authors}
#     #print(query)
#     if request.method == "POST":
#         author_name = request.POST.get('author_name', None)
#         context.update({"author_name": author_name})
#         errors = []
#
#         if author_name is not None:
#             print(author_name)
#             #
#
#             # The function below doesnt implement yet any jerkproof validations in case
#             # the author doesnt exist in the graph
#             listM1 = kwRecommendationM1(author_name)
#
#             # if path == 0:
#             #     errors.append("Path estimation: Either source or target node is not in KW graph")
#             # else:
#             #     if path == 1:
#             #         errors.append("No path between nodes")
#             # ##
#             # probRF = probOfConnectivity(keyword1, keyword2)
#             # if probRF == -1:
#             #     errors.append("Prob estimation: Either source or target node is not in KW graph")
#
#
#             if not errors:
#                 context.update({"listM1": listM1})
#             else:
#                 context.update({"errors": errors})
#
#     return render(request, 'keyword_recommendations.html', context)

def map(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = KeywordForm(request.POST)
        if form.is_valid():
            keywordQuery = validateString(form.cleaned_data.get('keyword'))
            yearQuery = validateString(form.cleaned_data.get('publication_year'))

            # THE METHOD BELOW USES DJANGO MODEL LAYER
            # queryset = Keyword_Publication.objects.all().select_related('id_keyword').select_related('id_publication')
            # queryset = queryset.filter(id_keyword__keyword__contains=keywordQuery).filter(id_publication__publication_date__year=yearQuery).values('id_publication')
            print(keywordQuery)
            print(yearQuery)
            print()

            # THE METHOD BELOW BYPASSES THE MODEL LAYER
            query = """SELECT f.affiliation, f.city, f.country, f.longitude, f.latitude
            FROM ntgBackend_publication a, ntgBackend_keyword_publication b, ntgBackend_keyword c,
            ntgBackend_author d, ntgBackend_publication_author e,
            ntgBackend_affiliation f, ntgBackend_publication_author_affiliation g
            WHERE c.keyword LIKE '%{0}%'
            AND c.id_keyword = b.id_keyword_id
            AND b.id_publication_id = a.id_publication
            AND YEAR(a.publication_date) = {1}
            AND a.id_publication = e.id_publication_id
            AND e.id_author_id = d.id_author
            AND e.id_publication_author = g.id_publication_author_id
            AND f.id_affiliation = g.id_affiliation_id
            AND affiliation != 'N/A'
            GROUP BY f.affiliation, f.city, f.country, f.longitude, f.latitude
            ORDER BY f.affiliation, f.city, f.country, f.longitude, f.latitude
            """.format(keywordQuery, yearQuery)

            print(query)

            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = dictfetchall(cursor)

            extra_context = {"results": rows, "form": form}
            return render(request, "map.html", extra_context)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = KeywordForm()
    return render(request, 'map.html', {'form': form})

def index(request):
    return render(request, 'home.html')

def chartViz(request):
    return render(request, 'chartViz.html')

def viz(request):
    context = {}
    graph = make_json('plasticity', ['2018'])
    context.update({"graph": graph})
    return render(request, 'vizTest3.html', context)

def test(request):

    # the query below could be avoided by using Django's model layer
    query = "SELECT id_affiliation, affiliation FROM ntgBackend_affiliation ORDER BY affiliation"
    with connection.cursor() as cursor:
        cursor.execute(query)
        affiliations = dictfetchall(cursor)
    context = {"affiliations": affiliations}



    if request.method == 'POST':
        # get values from form
        # We are expecting the following items:
        # and we need to check whether they're defined
        publicationForm = request.POST.get('publicationForm')
        publicationOption = request.POST.get('publicationOption')
        authorForm = request.POST.get('authorForm')
        authorOption = request.POST.get('authorOption')
        keywordForm = request.POST.get('keywordForm')
        keywordOption = request.POST.get('keywordOption')
        yearForm = request.POST.getlist('yearForm')
        yearOption = request.POST.get('yearOption')
        affiliationForm = request.POST.get('affiliationForm')
        affiliationOption = request.POST.get('affiliationOption')
        genderForm = request.POST.get('genderForm')
        genderOption = request.POST.get('genderOption')

        errors = []
        warnings = []
        queryNTG = False

        # Check that there's something to query about:
        if publicationOption:
            queryNTG = True
            context.update({"publicationOption": publicationOption})

        if authorOption:
            queryNTG = True
            context.update({"authorOption": authorOption})

        if keywordOption:
            queryNTG = True
            context.update({"keywordOption": keywordOption})

        if yearOption:
            queryNTG = True
            context.update({"yearOption": yearOption})

        if affiliationOption:
            queryNTG = True
            context.update({"affiliationOption": affiliationOption})

        if genderOption:
            queryNTG = True
            context.update({"genderOption": genderOption})

        if queryNTG == False:
            errors.append("Nothing to query about!")
        else:
            queryType = ""
            publicationQuery = ""
            authorQuery = ""
            keywordQuery = ""
            yearQuery = ""
            affiliationQuery = ""
            genderQuery = ""

        if publicationOption == 'in':
            if publicationForm == '':
                errors.append("Query by publication but no publication specified!")
            else:
                context.update({"publicationForm": publicationForm})
                publicationQuery = validateString(publicationForm)
        elif publicationOption == 'out':
            pass

        if authorOption == 'in':
            if authorForm == '':
                errors.append("Query by author but no author specified!")
            else:
                context.update({"authorForm": authorForm})
                authorQuery = validateString(authorForm)
        elif authorOption == 'out':
            if keywordOption == 'in':
                queryType = "graph"
            elif affiliationOption == 'in':
                queryType = "starGraph"

        if keywordOption == 'in':
            if keywordForm == '':
                errors.append("Query by keyword but no keyword specified!")
            else:
                context.update({"keywordForm": keywordForm})
                keywordQuery = validateString(keywordForm)
        elif keywordOption == 'out':
            queryType = "starGraph"

        if yearOption == 'in':
            if not yearForm:
                errors.append("Query by years but no year was specified!")
            else:
                context.update({"yearForm": yearForm})
                #iterate through all years in selection
                yearQuery = "AND (YEAR(a.publication_date) = "
                yearQuery = yearQuery + " OR YEAR(a.publication_date) = ".join(yearForm)
                yearQuery = yearQuery + ") "
        elif yearOption == 'out':
            pass

        if affiliationOption == 'in':
            if affiliationForm == '0':
                errors.append("Query by affiliation but no affiliation specified!")
            else:
                context.update({"affiliationForm": affiliationForm})
                queryType = "starGraph"
        elif affiliationOption == 'out':
            queryType = "map"

        if genderOption == 'in':
            if genderForm == '0':
                errors.append("Query by gender but no gender specified!")
            else:
                context.update({"genderForm": genderForm})
                genderQuery = "AND d.gender = '{0}'".format(genderForm)
        elif genderOption == 'out':
            queryType = "chart"

        if not errors:
            if queryType == "map":
                query = """
                SELECT f.affiliation, f.city, f.country, f.longitude, f.latitude
                FROM ntgBackend_publication a, ntgBackend_keyword_publication b, ntgBackend_keyword c,
                ntgBackend_author d, ntgBackend_publication_author e,
                ntgBackend_affiliation f, ntgBackend_publication_author_affiliation g
                WHERE c.keyword LIKE '%{0}%'
                AND c.id_keyword = b.id_keyword_id
                AND b.id_publication_id = a.id_publication {1} {2}
                AND a.id_publication = e.id_publication_id
                AND e.id_author_id = d.id_author
                AND e.id_publication_author = g.id_publication_author_id
                AND f.id_affiliation = g.id_affiliation_id
                AND affiliation != 'N/A'
                GROUP BY f.affiliation, f.city, f.country, f.longitude, f.latitude
                ORDER BY f.affiliation, f.city, f.country, f.longitude, f.latitude
                """.format(keywordQuery, yearQuery, genderQuery)

                print(query)

                with connection.cursor() as cursor:
                    cursor.execute(query)
                    if cursor.rowcount > 0:
                        results = dictfetchall(cursor)
                    else:
                        warnings.append("No results with search criteria!")
                        context.update({"warnings": warnings})
                if not warnings:
                    context.update({"resultsAffiliations": results})

            elif queryType == "graph":
                if not yearForm:
                    yearForm = []
                if genderForm == '0':
                    genderForm = ""
                graph, rawData = generateGraph(keywordForm, yearForm, genderForm)
                context.update({"graph": graph})
                context.update({"rawData": rawData})

            elif queryType == "starGraph":
                queryItems = {}

                if not yearForm:
                    yearForm = []
                if genderForm == '0':
                    genderForm = ""

                queryItems.update({"genderForm": genderForm})
                queryItems.update({"yearForm": yearForm})

                if authorOption == "in" and keywordOption == "out":
                    # query III
                    #graph = generateStarGraph(authorForm, yearForm, genderForm, "author")
                    queryItems.update({"authorForm": authorForm})
                    graph = generateStarGraph('author','keyword',queryItems)
                elif affiliationOption == "in" and keywordOption == "out":
                    # query IV
                    #graph = generateStarGraph(affiliationForm, yearForm, genderForm, "affiliation")
                    queryItems.update({"affiliationForm": affiliationForm})
                    graph = generateStarGraph('affiliation','keyword',queryItems)
                elif affiliationOption == "in" and authorOption == "out":
                    #query V
                    queryItems.update({"affiliationForm": affiliationForm})
                    graph = generateStarGraph('affiliation','author',queryItems)

                if graph == 0:
                    warnings.append("No results with search criteria!")
                    context.update({"warnings": warnings})
                else:
                    context.update({"graph": graph})

            elif queryType == "chart":
                queryItems = {}

                if genderOption == "out":
                    if keywordOption == "in":
                        queryItems.update({"keywordForm": keywordForm})
                        data = generateChart('keyword', 'gender', queryItems)
                    else:
                        # no KW specific-> count all authors
                        data = generateChart('none', 'gender', queryItems)
                if data == 0:
                    warnings.append("No results with search criteria!")
                    context.update({"warnings": warnings})
                else:
                    context.update({"chartResults": data})

        else:
            context.update({"errors": errors})

    return render(request, 'index.html', context)
