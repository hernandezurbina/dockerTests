from django import forms

yearOptions = (("2012", "2012"),
                ("2013", "2013"),
                ("2014", "2014"),
                ("2015", "2015"),
                ("2016", "2016"),
                ("2017", "2017"),
                ("2018", "2018"),)
queryOptions = [('in','In'), ('out','Out')]



class KeywordForm(forms.Form):
    keyword = forms.CharField(label='keyword', max_length=50)
    publication_year = forms.CharField(label='publication_year', max_length=4)

class mainSearchForm(forms.Form):
    publication = forms.CharField(label='Publication', max_length=100)
    pubInOut = forms.ChoiceField(label='',choices=queryOptions, widget=forms.RadioSelect())
    author = forms.CharField(label='Author', max_length=100)
    authorInOut = forms.ChoiceField(label='',choices=queryOptions, widget=forms.RadioSelect())
    keyword = forms.CharField(label='Keyword', max_length=100)
    keywordInOut = forms.ChoiceField(label='',choices=queryOptions, widget=forms.RadioSelect())
    years = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=yearOptions)
    yearsInOut = forms.ChoiceField(label='',choices=queryOptions, widget=forms.RadioSelect())
    # like = forms.ChoiceField(choices=queryOptions, widget=forms.RadioSelect())
    # CHOICES = (('Option 1', 'Option 1'),('Option 2', 'Option 2'),)
    # field = forms.ChoiceField(choices=CHOICES)
