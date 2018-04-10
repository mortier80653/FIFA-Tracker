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
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from core import views as core_views
from account_settings import views as account_settings_views
from accounts import views as accounts_views

urlpatterns = [
    url(r'^$', core_views.home, name='home'),
    url(r'^about/$', core_views.about, name='about'),
    url(r'^contact/$', core_views.contact, name='contact'),
    url(r'^donate/$', core_views.donate, name='donate'),
    url(r'^privacy-policy/$', core_views.privacypolicy, name='privacypolicy'),
    url(r'^upload/$', core_views.upload_career_save_file, name='upload_career_save_file'),
    url(r'^upload/process_status/$', core_views.process_status, name='process_status'),
    url(r'^login/$', accounts_views.login_view, name='login_view'),
    url(r'^signup/$', accounts_views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', accounts_views.activate, name='activate'),
    url(r'^reset-password/$', accounts_views.password_reset,  name='reset_password'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', accounts_views.reset, name='reset'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^players/', include('players.urls')),
    url(r'^transfers/', include('transfer_history.urls')),
    url(r'^teams/', include('teams.urls')),
    url(r'^settings/', include('account_settings.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n'), name='set_language'),
    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^debug/', include(debug_toolbar.urls)),
    ] 

