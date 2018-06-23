from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^calculator/$', views.calculator, name='calculator'),
    url(r'^calculator/ajax/calc-pot/$', views.ajax_calcpot, name='ajax_calcpot'),
    url(r'^calculator/ajax/calc-wage/$',
        views.ajax_calcwage, name='ajax_calcwage'),
]
