from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='edit_player', permanent=False)),
    url(r'^player/$', views.player, name='edit_player'),
    url(r'^player/(?P<playerid>\d{1,6})/$', views.player, name='edit_player_by_id'),
]