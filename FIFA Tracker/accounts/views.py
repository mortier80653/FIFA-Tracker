from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .forms import SignUpForm, LoginForm

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
        return redirect('home')

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
