from django.shortcuts import render
from .models import Players, Teamplayerlinks

def players(request):
    data = Players.objects.order_by('-potential')[:40]
    for obj in data:
        setattr(obj, 'clubid', Teamplayerlinks.objects.filter(playerid=obj.playerid).values('teamid')[0]['teamid'])

    return render(request, 'players.html', {'data':data})