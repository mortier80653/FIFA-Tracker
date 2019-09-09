import logging

from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from accounts.tasks import send_verification_email, send_password_reset_email
from celery.task.control import inspect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
import accounts.serializers as serializers

from core.session_utils import del_session_key
from .forms import SignUpForm, LoginForm, PasswordResetForm, SetNewPasswordForm
from .tokens import account_activation_token, reset_password_token


def signup(request):
    if request.user.is_authenticated:
        messages.error(request, _(
            "Hey {}, you are already logged in!").format(request.user))
        return redirect('home')

    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        # user.is_active = True
        user.save()

        current_site = get_current_site(request)
        subject = _('FIFA Tracker - Account activation')
        message = render_to_string('accounts/activate_email.html', {
            'user': user,
            'scheme': request.scheme,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        email_content = {
            'subject': subject,
            'message': message,
        }
        send_verification_email.delay(user.pk, email_content)

        messages.success(
            request,
            _('Confirmation link has been sent to {}. Make sure to check your spam folder')
            .format(form.cleaned_data['email'])
        )
        return redirect('home')

    return render(
        request,
        'accounts/signup.html',
        {'form': form}
    )


def login_view(request):
    if request.user.is_authenticated:
        messages.error(
            request,
            _("Hey {}, you are already logged in!").format(request.user)
        )

        return redirect('home')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        # clear guest data from session
        del_session_key(request, "career_user")

        user = form.login(request)
        if user is not None:
            login(request, user)
            messages.success(
                request,
                _("It's nice to see you again {}!").format(request.user)
            )

            return redirect('players')

    return render(
        request,
        'accounts/login.html',
        {'form': form}
    )


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, _(
            "Account activated! You can upload your FIFA career save now."))
        return redirect('upload_career_save_file')
    else:
        messages.error(
            request,
            _("The confirmation link was invalid, possibly because it has already been used.")
        )
        return redirect('home')


def password_reset(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = PasswordResetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()

        current_site = get_current_site(request)
        subject = _('FIFA Tracker - Password Reset')
        body = render_to_string('accounts/password_reset_email.html', {
            'user': user,
            'scheme': request.scheme,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': reset_password_token.make_token(user),
        })
        email_content = {
            'to': user.email,
            'subject': subject,
            'message': body,
        }

        c_task = send_password_reset_email.delay(email_content)
        # c_task1 = send_password_reset_email.delay(email_content)
        # c_task2 = send_password_reset_email.delay(email_content)
        # c_task3 = send_password_reset_email.delay(email_content)
        # c_task4 = send_password_reset_email.delay(email_content)
        # i = inspect(['celery@aranaktu-VirtualBox'])
        # from pprint import pprint as pp
        # import pdb
        # pdb.set_trace()

        user_email_address, user_email_domain = user.email.split('@')
        user_email_address = user_email_address[:1] + \
            '****' + user_email_address[-2:]
        messages.success(
            request,
            _("We've emailed you instructions for setting your new password, to {}")
            .format(user_email_address + '@' + user_email_domain)
        )

    return render(request, 'accounts/password_reset_form.html', {'form': form})


def reset(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and reset_password_token.check_token(user, token):
        form = SetNewPasswordForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            new_password = form.cleaned_data['new_password2']
            user.set_password(new_password)
            user.save()
            messages.success(
                request,
                _('Password has been reset. You can login now using your new credentials.')
            )
            return redirect('home')
        else:
            return render(request, 'accounts/password_set_new.html', {'form': form})
    else:
        messages.error(request, 'The reset password link is no longer valid.')
        return redirect('home')


class UserRequestPasswordReset(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            if 'username' in request.data:
                user = User.objects.get(username=request.data['username'])
            elif 'email' in request.data:
                user = User.objects.get(email=request.data['email'])
            else:
                return Response(
                    {'msg': 'Username or Email is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            send_password_reset_email.delay(
                user.pk,
                request.scheme,
                get_current_site(request).domain
            )
            user_email_address, user_email_domain = user.email.split('@')
            user_email_address = user_email_address[:1] + \
                                 '****' + user_email_address[-2:]
            msg = _(
                "We've emailed you instructions for setting your new password, to {}"
            ).format(user_email_address + '@' + user_email_domain)

            return Response(
                {'msg': msg},
                status=status.HTTP_200_OK
            )
        except (KeyError,  User.DoesNotExist):
            return Response(
                {'msg': _("Sorry, account doesn't exists in our database. Please try again.")},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserPasswordReset(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = serializers.PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uidb64 = request.data['uidb64']
                token = request.data['token']

                uid = force_text(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except Exception as e:
                logging.exception("UserPasswordReset error")
                user = None

            token_is_valid = reset_password_token.check_token(user, token)
            if (user is None) or (not token_is_valid):
                return Response({'msg': 'Invalid user or token.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(request.data['new_password'])
            user.save()
            return Response(
                {'msg': _('Password has been reset. You can login now using your new credentials.')},
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserActivate(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            uidb64 = request.data['uidb64']
            token = request.data['token']

            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception as e:
            logging.exception("UserActivate error")
            user = None

        token_is_valid = account_activation_token.check_token(user, token)
        if (user is None) or (not token_is_valid):
            return Response({'msg': 'Invalid user or token.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()
        return Response({'msg': 'Account activated, you can login now.'}, status=status.HTTP_200_OK)


class UserCreate(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):

        serializer = serializers.UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            send_verification_email.delay(
                serializer.data['username'],
                request.scheme,
                get_current_site(request).domain
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        user = authenticate(**request.data)

        if user and user.is_active:
            token = RefreshToken.for_user(user)
            return Response({
                'refresh': str(token),
                'access': str(token.access_token),
            }, status=status.HTTP_200_OK)
        elif 'username' in request.data:
            user = User.objects.filter(username__iexact=request.data['username']).first()

            if user and not user.is_active:
                return Response(
                    {
                        'detail': "Account not activated",
                        'code': "account_not_active",
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

        return Response(
            {
                'detail': "Invalid username or password",
                'code': "invalid_credentials",
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def current_user(request):
    """
    Determine the current user by their token, and return their data
    """

    serializer = serializers.UserSerializer(request.user)
    return Response(serializer.data)
