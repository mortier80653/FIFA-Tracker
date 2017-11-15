from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm

from .forms import SignUpForm

def signup(request):
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
    icons = {"username": "glyphicon-user", "password": "glyphicon-lock"}
    
    form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form, 'icons': icons })
