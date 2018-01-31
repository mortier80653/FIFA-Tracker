from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.settings, name='settings'),
    url(r'^ajax/change-currency/$', views.ajax_change_currency, name='change_currency'),
    url(r'^ajax/change-unit-system/$', views.ajax_change_unit_system, name='change_unit_system'),
]