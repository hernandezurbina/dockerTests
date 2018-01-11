from django.contrib import admin
from polls.models import Question
from polls.models import Choice

admin.site.register(Question)
admin.site.register(Choice)
# Register your models here.
