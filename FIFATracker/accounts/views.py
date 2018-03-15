from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib import messages

from .forms import SignUpForm, LoginForm, PasswordResetForm, SetNewPasswordForm
from .tokens import account_activation_token, reset_password_token


def signup(request):
    if request.user.is_authenticated:
        messages.error(request, "Hey {}, you are already logged in!".format(request.user))
        return redirect('home')

    icons = {"username": "glyphicon-user", "email": "glyphicon-envelope", "password1": "glyphicon-lock", "password2": "glyphicon-lock"}

    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        #user.is_active = True
        user.save()
        '''
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user_auth = authenticate(username=username, password=raw_password)
        login(request, user_auth)
        return redirect('home')
        '''
        current_site = get_current_site(request)
        subject = 'FIFA Tracker - Account activation'
        message = render_to_string('accounts/activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'token': account_activation_token.make_token(user),
        })
        user.email_user(subject, message)
        messages.success(request, 'Confirmation link has been sent to {}. Make sure to check your spam folder'.format(form.cleaned_data['email']))
        return redirect('home')
        #'''

    return render(request, 'accounts/signup.html', {'form': form, 'icons': icons })

def login_view(request):
    if request.user.is_authenticated:
        messages.error(request, "Hey {}, you are already logged in!".format(request.user))
        return redirect('home')

    icons = {"username": "glyphicon-user", "password": "glyphicon-lock"}  

    form = LoginForm(request.POST or None)  
    if request.method == 'POST' and form.is_valid():
        user = form.login(request)
        if user is not None:
            login(request, user)
            messages.success(request, "It's nice to see you again {}!".format(request.user))
            return redirect('players')
    
    return render(request, 'accounts/login.html', {'form': form, 'icons': icons })


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
        messages.success(request, "Account activated! You can upload your FIFA career save now.")
        return redirect('upload_career_save_file')
    else:
        messages.error(request, "The confirmation link was invalid, possibly because it has already been used.")
        return redirect('home')


def password_reset(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = PasswordResetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()

        current_site = get_current_site(request)
        subject = 'FIFA Tracker - Password Reset'
        body = render_to_string('accounts/password_reset_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'token': reset_password_token.make_token(user),
        })
        email = EmailMessage(subject, body, to=[user.email])
        email.send()
        user_email_address, user_email_domain = user.email.split('@')
        user_email_address = user_email_address[:1] + '****' + user_email_address[-2:]
        messages.success(request, "We've emailed you instructions for setting your new password, to {}".format(user_email_address + '@' + user_email_domain))

    return render(request, 'accounts/password_reset_form.html', {'form':form})

def reset(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and reset_password_token.check_token(user, token):
        form = SetNewPasswordForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            new_password= form.cleaned_data['new_password2']
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password has been reset. You can login now using your new credentials.')
            return redirect('home')
        else:
            return render(request, 'accounts/password_set_new.html', {'form':form})
    else:
        messages.error(request, 'The reset password link is no longer valid.')
        return redirect('home')
