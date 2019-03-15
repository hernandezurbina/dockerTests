import json
from django.db import connection
from ntgFrontend.validations import validateString

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def generateChart(queryIn, queryOut, queryItems):
    if queryIn == "keyword" and queryOut == "gender":
        keywordQuery = validateString(queryItems["keywordForm"])

        queryYears = """
        SELECT YEAR(publication_date) as publication_year
        FROM ntgBackend_publication
        GROUP BY publication_year
        ORDER BY publication_year
        """

        queryGenders = """
        SELECT gender
        FROM ntgBackend_author
        GROUP BY gender
        ORDER BY gender
        """

        queryCounts = """
        SELECT COUNT(*) FROM(
        SELECT a.author_name
        FROM ntgBackend_author a, ntgBackend_publication_author b, ntgBackend_publication c,
        ntgBackend_keyword_publication d, ntgBackend_keyword e
        WHERE YEAR(c.publication_date) = {0}
        AND a.id_author = b.id_author_id AND c.id_publication = b.id_publication_id
        AND a.gender = '{1}'
        AND e.keyword LIKE '%{2}%'
        AND e.id_keyword = d.id_keyword_id
        AND d.id_publication_id = c.id_publication
        GROUP BY a.author_name
        ORDER BY a.author_name) AS numAuthors
        """

        # GET ALL YEARS!
        with connection.cursor() as cursor:
            cursor.execute(queryYears)
            if cursor.rowcount > 0:
                cursorYears = cursor.fetchall()
            else:
                return 0

        # GET ALL GENDERS!
        with connection.cursor() as cursor:
            cursor.execute(queryGenders)
            if cursor.rowcount > 0:
                cursorGenders = cursor.fetchall()
            else:
                return 0


        years = []
        genders = []
        counts = []

        # GET ALL COUNTS PER YEAR AND GENDER
        for rowYears in cursorYears:
            year = rowYears[0]
            for rowGenders in cursorGenders:
                years.append(year)
                gender = rowGenders[0]
                genders.append(gender)
                # RUN QUERY
                with connection.cursor() as cursor:
                    cursor.execute(queryCounts.format(year, gender, keywordQuery))
                    if cursor.rowcount > 0:
                        counts.append(cursor.fetchone()[0])
                    else:
                        return 0

        return genJsonChart(genders, years, counts)


def generateStarGraph(queryIn, queryOut, queryItems):
    if not queryItems["yearForm"]:
        yearQuery = ""
    else:
        yearQuery = "AND (YEAR(a.publication_date) = "
        yearQuery = yearQuery + " OR YEAR(a.publication_date) = ".join(queryItems["yearForm"])
        yearQuery = yearQuery + ") "

    if not queryItems["genderForm"]:
        genderQueryFrom = ""
        genderQueryWhere = ""
        genderQuery = ""
    else:
        if queryIn == "affiliation" and queryOut == "keyword":
            genderQueryFrom = "ntgBackend_author d,"
            genderQueryWhere = "AND e.id_author_id = d.id_author AND d.gender = '{0}'".format(queryItems["genderForm"])
        elif queryIn == "affiliation" and queryOut == "author":
            genderQuery = "AND d.gender = '{0}'".format(queryItems["genderForm"])

    if queryIn == "affiliation" and queryOut == "author":
        affiliationQuery = queryItems["affiliationForm"]
        query = """
        SELECT d.author_name, COUNT(*) as occurrences, f.affiliation
        FROM ntgBackend_publication a,
        ntgBackend_author d, ntgBackend_publication_author e, ntgBackend_affiliation f,
        ntgBackend_publication_author_affiliation g
        WHERE f.id_affiliation = {0}
        AND f.id_affiliation = g.id_affiliation_id
        AND g.id_publication_author_id = e.id_publication_author
        AND e.id_publication_id = a.id_publication {1}
        AND e.id_author_id = d.id_author {2}
        GROUP BY d.author_name, f.affiliation
        ORDER BY d.author_name, f.affiliation
        """.format(affiliationQuery, yearQuery, genderQuery)

    elif queryIn == "author" and queryOut == "keyword":
        authorQuery = validateString(queryItems["authorForm"])
        query = """
        SELECT c.keyword, COUNT(*) as occurrences
        FROM ntgBackend_publication a, ntgBackend_keyword_publication b, ntgBackend_keyword c,
        ntgBackend_author d, ntgBackend_publication_author e
        WHERE d.id_author = e.id_author_id
        AND b.id_publication_id = e.id_publication_id
        AND b.id_keyword_id = c.id_keyword
        AND d.author_name LIKE '%{0}%' {1}
        AND a.id_publication = e.id_publication_id
        GROUP BY c.keyword
        ORDER BY c.keyword
        """.format(authorQuery, yearQuery)

    elif queryIn == "affiliation" and queryOut == "keyword":
        affiliationQuery = queryItems["affiliationForm"]
        query = """
        SELECT c.keyword, COUNT(*) as occurrences, f.affiliation
        FROM ntgBackend_publication a, ntgBackend_keyword_publication b,
        ntgBackend_keyword c, {0} ntgBackend_publication_author e, ntgBackend_affiliation f,
        ntgBackend_publication_author_affiliation g
        WHERE f.id_affiliation = {1}
        AND f.id_affiliation = g.id_affiliation_id
        AND g.id_publication_author_id = e.id_publication_author
        AND e.id_publication_id = a.id_publication
        AND a.id_publication = b.id_publication_id
        AND b.id_keyword_id = c.id_keyword {2} {3}
        GROUP BY c.keyword, f.affiliation
        ORDER BY c.keyword, f.affiliation
        """.format(genderQueryFrom, affiliationQuery, yearQuery, genderQueryWhere)

    data = {}
    print(query)

    with connection.cursor() as cursor:
        cursor.execute(query)
        if cursor.rowcount > 0:
            rows = cursor.fetchall()
        else:
            return 0

    for row in rows:
        if queryIn == "affiliation":
            uid = row[2]
        elif queryIn == "author":
            uid = queryItems["authorForm"]

        try:
            data[uid]['keyword'].append(row[0])
            data[uid]['occurrences'].append(float(row[1]))
        except KeyError:
            data[uid] = {'keyword': [row[0]],
                         'occurrences': [float(row[1])]}

    return genJsonStarGraph(uid, data[uid]['keyword'], word_type=queryIn, field_type='keyword', field_strength=data[uid]['occurrences'])


def getByKeywordFromDB(keyword, years, gender):

    if not years:
        yearQuery = ""
    else:
        yearQuery = "AND (YEAR(a.publication_date) = "
        yearQuery = yearQuery + " OR YEAR(a.publication_date) = ".join(years)
        yearQuery = yearQuery + ") "

    if not gender:
        genderQuery = ""
    else:
        genderQuery = "AND d.gender = '{0}'".format(gender)

    keywordQuery = validateString(keyword)

    data = {}

    # query = """
    # SELECT a.title, a.id_publication, d.author_name, f.score
    # FROM ntgBackend_publication a, ntgBackend_keyword_publication b, ntgBackend_keyword c,
    # ntgBackend_author d, ntgBackend_publication_author e,
    # ntgBackend_authorscore f
    # WHERE c.keyword LIKE '%{0}%'
    # AND c.id_keyword = b.id_keyword_id
    # AND b.id_publication_id = a.id_publication {1} {2}
    # AND a.id_publication = e.id_publication_id
    # AND e.id_author_id = d.id_author
    # AND f.publication_year = YEAR(a.publication_date)
    # AND f.id_author_id = d.id_author
    # GROUP BY a.title, a.id_publication, d.author_name, f.score
    # ORDER BY a.title, a.id_publication, d.author_name, f.score
    # """.format(keywordQuery, yearQuery, genderQuery)


    # BELOW QUERY FOR GRAPH!
    # Different from the one above because the SELECT statement changes!
    # In the query below we are not grouping by same select statement!
    query = """
    SELECT a.title, CONCAT("Year: ", YEAR(a.publication_date), ". ID: ", a.other_id, ". ", a.title) AS info, d.author_name, f.score
    FROM ntgBackend_publication a, ntgBackend_keyword_publication b, ntgBackend_keyword c,
    ntgBackend_author d, ntgBackend_publication_author e,
    ntgBackend_authorscore f
    WHERE c.keyword LIKE '%{0}%'
    AND c.id_keyword = b.id_keyword_id
    AND b.id_publication_id = a.id_publication {1} {2}
    AND a.id_publication = e.id_publication_id
    AND e.id_author_id = d.id_author
    AND f.publication_year = YEAR(a.publication_date)
    AND f.id_author_id = d.id_author
    GROUP BY a.title, a.id_publication, d.author_name, f.score
    ORDER BY a.title, a.id_publication, d.author_name, f.score
    """.format(keywordQuery, yearQuery, genderQuery)

    print(query)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    for ii,row in enumerate(rows):
        uid = row[1]
        try:
            data[uid]['authors'].append(row[2])
            data[uid]['score'].append(float(row[3]))
        except KeyError:
            data[uid] = {'title': row[0],
                         'authors': [row[2]],
                         'score': [float(row[3])]}

    # BELOW QUERY FOR DETAILS!
    query = """
    SELECT a.id_publication, a.title, d.author_name, YEAR(a.publication_date) AS publication_year, a.other_id AS cosyne_id
    FROM ntgBackend_publication a, ntgBackend_keyword_publication b, ntgBackend_keyword c,
    ntgBackend_author d, ntgBackend_publication_author e,
    ntgBackend_authorscore f
    WHERE c.keyword LIKE '%{0}%'
    AND c.id_keyword = b.id_keyword_id
    AND b.id_publication_id = a.id_publication {1} {2}
    AND a.id_publication = e.id_publication_id
    AND e.id_author_id = d.id_author
    AND f.publication_year = YEAR(a.publication_date)
    AND f.id_author_id = d.id_author
    GROUP BY a.id_publication, a.title, d.author_name, publication_year, cosyne_id
    ORDER BY publication_year, a.title, d.author_name
    """.format(keywordQuery, yearQuery, genderQuery)

    print(query)

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = dictfetchall(cursor)


    return data, rows

def make_author_dict(data):
    auth_dict = {}
    for item in data:
        for ii,auth in enumerate(data[item]['authors']):
            try:
                auth_dict[auth]['titles'].append(item)
            except KeyError:
                auth_dict[auth] = {'titles': [item],
                                   'score': data[item]['score'][ii]}
    return auth_dict

def genJsonStarGraph(word, fields, word_type='author', field_type='keyword', field_strength=None):
    '''word can be an author, fields is a list can be the keywords
    associated with them or word can be a title, fields is a list can
    be the authors associated with it or word can be a title, fields
    is a list can be the keywords associated with it or word can be an
    year, fields is a list of keywords
    word_type is either author, title, or year, co_auth,
    field_strength is a list like fields but has floats
    which correspond to the strengths of the field
    '''

    j_dict = {"graph": {},
              "directed": False,
              "multigraph": False}
    j_dict["nodes"] = []
    n = j_dict["nodes"]
    j_dict["links"] = []
    l = j_dict["links"]
    json_group_dict = {'title': 0, 'keyword': 1, 'author': 2, 'affiliation': 3, 'year': 4}
    n.append({"id": word,
              "group": json_group_dict[word_type],
              "size":10,
              "titles":[]})
    if field_strength is None:
        for jj, field in enumerate(fields):
            n.append({"id": field,
                      "group": json_group_dict[field_type],
                      "size":10,
                      "titles":[]})
            l.append({"source": 0,
                      "target": jj + 1,
                      "weight": 5.})
    else:
        for jj, field in enumerate(fields):
            n.append({"id": field,
                      "group": json_group_dict[field_type],
                      "size": field_strength[jj],
                      "titles":[]})
            l.append({"source": 0,
                      "target": jj + 1,
                      "weight": 5.})
    return json.dumps(j_dict)

def genJsonChart(labels, xaxis_pts, yaxis_pts):
    #assert len(labels) == len(yaxis_pts)
    #assert len(xaxis_pts) == len(yaxis_pts)
    unique_years = set(xaxis_pts)
    pre = {}
    for ii, label in enumerate(labels):
        try:
            pre[label].append(xaxis_pts[ii])
        except:
            pre[label] = [xaxis_pts[ii]]
    fix = {}
    for item in pre:
        this_ent = pre[item]
        not_exist = [ent for ent in unique_years if ent not in this_ent]
        fix[item] = not_exist
    points_dict = []
    for ii, label in enumerate(labels):
        points_dict.append({"symbol": label,
                            "date": str(xaxis_pts[ii]),
                            "price": yaxis_pts[ii]})
    for item in fix:
        not_exist = fix[item]
        for jj in not_exist:
            points_dict.append({"symbol": item,
                                "date": str(jj),
                                "price": 10})

    return json.dumps(points_dict)


def generateGraph(keyword, years, gender):
    data, rawData = getByKeywordFromDB(keyword, years, gender)
    auth_dict = make_author_dict(data)
    j_dict = {"graph": {},
              "directed": False,
              "multigraph": False}
    j_dict["nodes"] = []
    n = j_dict["nodes"]
    keystring = keyword.upper()
    n.append({"id": keystring,
              "group": 1,
              "size":10,
              "titles":[]})
    j_dict["links"] = []
    l = j_dict["links"]
    exist_names = []
    pi_names = []
    for uid in data:
        auth_scores = data[uid]['score']
        pi_idx = auth_scores.index(max(auth_scores))
        pi_name = data[uid]['authors'][pi_idx]
        if pi_name not in pi_names:
            l.append({"source": 0,
                      "target": len(exist_names) + 1,
                      "weight": 5.})
            exist_names.append(pi_name)
            pi_names.append(pi_name)
            n.append({"id": pi_name,
                      "group": 2,
                      "size": auth_dict[pi_name]['score'],
                      "titles":auth_dict[pi_name]['titles']})
    for uid in data:
        auth_scores = data[uid]['score']
        pi_idx = auth_scores.index(max(auth_scores))
        pi_name = data[uid]['authors'][pi_idx]
        co_auths = data[uid]['authors']
        chelas = list(set(co_auths) - set([co_auths[pi_idx]]))
        for chela in chelas:
            if chela not in exist_names:
                l.append({"source": pi_names.index(pi_name) + 1,
                          "target": len(exist_names) + 1,
                          "weight": 5.})
                n.append({"id": chela,
                          "group": 3,
                          "size": auth_dict[chela]['score'],
                          "titles":auth_dict[chela]['titles']})
                exist_names.append(chela)
            else:
                l.append({"source": pi_names.index(pi_name) + 1,
                          "target": exist_names.index(chela) + 1,
                          "weight": 5.})

    return json.dumps(j_dict), rawData
