from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User

from .forms import SignUpForm, LoginForm
from .tokens import account_activation_token


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    icons = {"username": "glyphicon-user", "email": "glyphicon-envelope", "password1": "glyphicon-lock", "password2": "glyphicon-lock"}

    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'accounts/success.html')

        '''
        user.is_active = False
        user.save()
        current_site = get_current_site(request)
        subject = 'FIFA Tracker - Account activation'
        message = render_to_string('accounts/activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'token': account_activation_token.make_token(user),
        })
        user.email_user(subject, message)
        return render(request, 'accounts/account_activation_sent.html')
        '''

    return render(request, 'accounts/signup.html', {'form': form, 'icons': icons })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    icons = {"username": "glyphicon-user", "password": "glyphicon-lock"}  

    form = LoginForm(request.POST or None)  
    if request.method == 'POST' and form.is_valid():
        user = form.login(request)
        if user is not None:
            login(request, user)
            return redirect('players')
    
    return render(request, 'accounts/login.html', {'form': form, 'icons': icons })

def account_activation_sent(request):
    return render(request, 'accounts/account_activation_sent.html')

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
        return redirect('home')
    else:
        return render(request, 'accounts/account_activation_invalid.html')
