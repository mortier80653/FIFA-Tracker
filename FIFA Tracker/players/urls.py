from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.players, name='players'),
    url(r'^(?P<playerid>\d{1,6})/$', views.player, name='player'),
    url(r'^ajax/nationality/$', views.ajax_nationality, name='ajax_nationality'),
    url(r'^ajax/teams/$', views.ajax_teams, name='ajax_teams'),
]