from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Prefetch
from django.contrib.auth.models import User
from django.db import connection

from core.exceptions import NoResultsError, PrivateProfileError, UnknownError
from core.generate_view_helper import get_team, get_teams 

from players.models import (
    DataUsersTeams, 
    DataUsersLeagueteamlinks, 
    DataUsersLeagues, 
)

def teams(request):
    try:
        context = get_teams(request, paginate=True)
        return render(request, 'teams/teams.html', context=context)
    except (NoResultsError, PrivateProfileError, UnknownError) as e:
        messages.error(request, e)
        return redirect('home')
    
def team(request, teamid):
    try:
        context = get_team(request, teamid=teamid)
        return render(request, 'teams/team.html', context=context)
    except (NoResultsError, PrivateProfileError, UnknownError) as e:
        messages.error(request, e)
        return redirect('teams')
    