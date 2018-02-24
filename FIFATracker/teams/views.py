from functools import reduce

from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db import connection

from core.exceptions import NoResultsError, PrivateProfileError, UnknownError
from core.generate_view_helper import get_team, get_teams 

from players.models import (
    DataUsersTeams, 
    DataUsersLeagueteamlinks, 
    DataUsersLeagues, 
)

def ajax_team_by_name(request):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "guest"

    teams_found = list()

    teamname = request.GET.get('teamname', None)
    if teamname and len(teamname) > 1:
        teamname = teamname.split() # split space
        query = reduce(lambda x, y: x | y, [Q(teamname__unaccent__icontains=name) for name in teamname])

        teams = list(DataUsersTeams.objects.for_user(current_user).filter(query).all().order_by('-overallrating', 'teamid')[:12].iterator())

        for team in teams:
            t = dict()
            t['teamid'] = team.teamid
            t['overallrating'] = team.overallrating
            t['teamname'] = team.teamname
            teams_found.append(t)

    data = {
        'teams': teams_found,
    }

    return JsonResponse(data)

def ajax_leagues(request):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "guest"

    selected = request.GET.get('selected', None)

    if selected:
        selected = list(selected.split(","))
        leagues = list(DataUsersLeagues.objects.for_user(current_user).all().filter(Q(leagueid__in=selected)).values())
    else:
        leagues = list(DataUsersLeagues.objects.for_user(current_user).all().values())

    data = {
        'leagues': leagues,
    }

    return JsonResponse(data)

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
    