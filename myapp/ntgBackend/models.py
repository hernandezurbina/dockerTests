from django.db import models

class PublisherType(models.Model):
    id_publishertype = models.AutoField(primary_key=True)
    publisher_type = models.CharField(max_length=30)

class Publisher(models.Model):
    id_publisher = models.AutoField(primary_key=True)
    id_publishertype = models.ForeignKey(PublisherType, on_delete=models.CASCADE)
    publisher_name = models.CharField(max_length=50)
    issn = models.CharField(max_length=30, null=True)
    publishing_group = models.CharField(max_length=50, null=True)
    publication_year = models.PositiveSmallIntegerField(null=True)
    website = models.URLField(null=True)
    impact_factor = models.PositiveSmallIntegerField(null=True)

class Keyword(models.Model):
    id_keyword = models.AutoField(primary_key=True)
    keyword = models.CharField(max_length=50)

class Publication(models.Model):
    id_publication = models.AutoField(primary_key=True)
    id_publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    abstract = models.TextField()
    publication_date = models.DateField()
    pmcid = models.CharField(max_length=30, blank=True, null=True)
    pmid = models.CharField(max_length=30, blank=True, null=True)
    doi = models.CharField(max_length=30, blank=True, null=True)
    other_id = models.CharField(max_length=30, blank=True, null=True)
    contact_email = models.CharField(max_length=50, blank=True, null=True)
    citations = models.PositiveIntegerField(blank=True, null=True)
    keywords = models.ManyToManyField(Keyword, through='Keyword_Publication')

class Affiliation(models.Model):
    id_affiliation = models.AutoField(primary_key=True)
    affiliation = models.CharField(max_length=100)
    grid = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    website = models.CharField(max_length=200, blank=True, null=True)


class KeywordAlias(models.Model):
    id_keywordalias = models.AutoField(primary_key=True)
    id_keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    alias = models.CharField(max_length=50)

class Keyword_Publication(models.Model):
    # The primary key below was created to avoid Django creating an auto-generated PK
    id_keyword_publication = models.AutoField(primary_key=True)
    #id_publication = models.ForeignKey(Publication, related_name='id_keyword_publication', on_delete=models.CASCADE)
    id_publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    id_keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    #id_keyword = models.ForeignKey(Keyword, related_name='id_keyword_publication', on_delete=models.CASCADE)

    class Meta:
        unique_together = ("id_publication", "id_keyword")

class Author(models.Model):
    id_author = models.AutoField(primary_key=True)
    author_name = models.CharField(max_length=50)
    email = models.CharField(unique=True, max_length=50)
    gender = models.CharField(max_length=10, blank=True, null=True)
    current_affiliation = models.ForeignKey(Affiliation, on_delete=models.CASCADE)

class AuthorAlias(models.Model):
    id_authoralias = models.AutoField(primary_key=True)
    id_author = models.ForeignKey(Author, on_delete=models.CASCADE)
    alias = models.CharField(max_length=30)

class AuthorScore(models.Model):
    id_authorscore = models.AutoField(primary_key=True)
    score = models.IntegerField(blank=True, null=True)
    publication_year = models.PositiveSmallIntegerField(blank=True, null=True)
    id_author = models.ForeignKey(Author, on_delete=models.CASCADE)


class Publication_Author(models.Model):
    # The primary key below was created to avoid Django creating an auto-generated PK
    id_publication_author = models.AutoField(primary_key=True)
    id_publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    id_author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("id_publication", "id_author")

class Publication_Author_Affiliation(models.Model):
    # The primary key below was created to avoid Django creating an auto-generated PK
    id_publication_author_affiliation = models.AutoField(primary_key=True)
    id_publication_author = models.ForeignKey(Publication_Author, on_delete=models.CASCADE)
    id_affiliation = models.ForeignKey(Affiliation, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("id_publication_author", "id_affiliation")
