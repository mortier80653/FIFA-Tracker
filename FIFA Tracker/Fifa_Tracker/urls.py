"""Fifa_Tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from core import views as core_views
from accounts import views as accounts_views

urlpatterns = [
    url(r'^$', core_views.home, name='home'),
    url(r'^signup/$', accounts_views.signup, name='signup'),
    url(r'^login/$', accounts_views.login_view, name='login_view'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^players/', include('players.urls')),
    #url(r'^login/', user_views.login, name='login'),
    url(r'^admin/', admin.site.urls),
]
