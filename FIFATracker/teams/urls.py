from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.teams, name='teams'),
    url(r'^(?P<teamid>\d{1,6})/$', views.team, name='team'),
]