import time

from django.shortcuts import render, redirect
from .models import *
from django.db import connection

from .fifa_utils import FifaPlayer, PlayerAge, PlayerValue, PlayerWage, FifaDate

def players(request):
    start = time.time()

    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "test123"

    #data = list(DataUsersPlayers.objects.for_user(current_user).filter(preferredposition1=23).order_by('-overallrating')[:50].iterator())
    data = DataUsersPlayers.objects.for_user(current_user).filter(preferredposition1=23).order_by('-overallrating')[:50]
    # Current date according to in-game calendar
    current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate

    players = list()
    for player in data:
        players.append(FifaPlayer(player,current_user, current_date))

    endtime = time.time() - start # DEBUG
    print ("Loading time: {} Queries: {}".format(endtime, len(connection.queries))) #DEBUG
    return render(request, 'players/players.html', {'players':players})


def player(request, playerid):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "test123"

    data = DataUsersPlayerloans.objects.for_user(current_user).get(playerid=playerid)
    #print(dir(data))
    return render(request, 'players/player.html', {'data':data})