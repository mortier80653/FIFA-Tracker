from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.settings, name='settings'),
    url(r'^ajax/change_currency/$', views.ajax_change_currency, name='change_currency'),
    url(r'^ajax/change_unit_system/$', views.ajax_change_unit_system, name='change_unit_system'),
]