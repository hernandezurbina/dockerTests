from django.conf.urls import url
from . import views

urlpatterns = [
    #url(r'^$', views.index, name='index'),
    url(r'^$', views.test, name='test'),
    url(r'^test$', views.test, name='test'),
    # url(r'^keyword-path$', views.keyword_path, name='keyword_path'),
    # url(r'^keyword-recommendations$', views.keyword_recommendations, name='keyword_recommendations'),
    url(r'^map$', views.map, name='map'),
    url(r'^viz$', views.viz, name='viz'),
    url(r'^chartViz$', views.chartViz, name='chartViz'),
    url(r'^pubDetails$', views.pubDetails, name='pubDetails')
]
