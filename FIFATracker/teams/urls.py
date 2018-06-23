from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.teams, name='teams'),
    url(r'^(?P<teamid>\d{1,6})/$', views.team, name='team'),
    url(r'^ajax/leagues/$', views.ajax_leagues, name='ajax_leagues'),
    url(r'^ajax/team-by-name/$', views.ajax_team_by_name, name='ajax_team_by_name'),
]
