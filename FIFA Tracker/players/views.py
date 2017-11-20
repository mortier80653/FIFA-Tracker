from django.shortcuts import render
from .models import Players

def players(request):
    data = Players.objects.order_by('-potential')[:20]
    return render(request, 'players.html', {'data':data})