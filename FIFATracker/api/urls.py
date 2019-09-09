from django.conf.urls import url, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from . import views
from accounts.views import (
    UserLogin,
    UserCreate,
    UserActivate,
    UserRequestPasswordReset,
    UserPasswordReset
)
from file_uploads.views import CareerSaveFileUploadView
from core.views import CareerSavesGet, CareerSaveDelete

app_name = 'api'
urlpatterns = [
    url(r'^$', views.api_root, name='api-root'),
    url(r'^user/login/', UserLogin.as_view(), name="user_login"),
    url(r'^user/token_refresh/', TokenRefreshView.as_view(), name="user_token_refresh"),
    url(
        r'^user/create/$',
        UserCreate.as_view(),
        name='user_create',
    ),
    url(
        r'^user/activate/$',
        UserActivate.as_view(),
        name='user_activate',
    ),
    url(
        r'^user/request_password_reset/$',
        UserRequestPasswordReset.as_view(),
        name='user_request_password_reset',
    ),
    url(
        r'^user/confirm_password_reset/$',
        UserPasswordReset.as_view(),
        name='user_confirm_password_reset',
    ),
    url(
        r'^my_careers/upload_cm_save/$',
        CareerSaveFileUploadView.as_view(),
        name='upload_cm_save',
    ),
    url(
        r'^my_careers/get/$',
        CareerSavesGet.as_view(),
        name='my_careers_get',
    ),
    url(
        r'^my_careers/delete/$',
        CareerSaveDelete.as_view(),
        name='my_careers_delete',
    ),
]
