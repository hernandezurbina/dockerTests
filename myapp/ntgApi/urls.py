from django.conf.urls import url, include
from rest_framework import routers
# from rest_framework_swagger.views import get_swagger_view
from . import views


# schema_view = get_swagger_view(title='NTG API')

urlpatterns = [
    url(r'^publication-detail$', views.publication_detail),
    url(r'^$', views.publications),
    url(r'^publications/$', views.publications),
    url(r'^knowledge-path$', views.knowledge_path),
    # url(r'^docs/', schema_view),
]
