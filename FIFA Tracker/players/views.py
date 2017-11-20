from django.shortcuts import render

def players(request):
    return render(request, 'players.html')