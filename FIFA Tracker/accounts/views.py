from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .forms import SignUpForm

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    icons = {"username": "glyphicon-user", "email": "glyphicon-envelope", "password1": "glyphicon-lock", "password2": "glyphicon-lock"}

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form, 'icons': icons })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    icons = {"username": "glyphicon-user", "password": "glyphicon-lock"}    
    if request.method == 'POST':
        form = AuthenticationForm(None, request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form, 'icons': icons })
