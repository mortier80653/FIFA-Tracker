import time
from functools import reduce

from django.db.models import Q
from django.shortcuts import render, redirect
from django.db import connection

from .models import DataUsersPlayers, DataUsersTeamplayerlinks, DataUsersPlayerloans, DataUsersEditedplayernames, DataUsersTeams, DataUsersLeagueteamlinks, DataUsersCareerCalendar, DataUsersLeagues
from .fifa_utils import FifaPlayer


def players(request):
    start = time.time()

    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "test123"

    data = list(DataUsersPlayers.objects.for_user(current_user).filter(preferredposition1=5).select_related('firstname', 'lastname', 'playerjerseyname', 'commonname','nationality',).order_by('-potential')[:100].iterator())

    if len(data) <= 0:
        return render(request, 'players/players.html')

    dict_cached_queries = dict()
    dict_cached_queries['q_team_player_links'] = list(DataUsersTeamplayerlinks.objects.for_user(current_user).filter(reduce(lambda x, y: x | y, [Q(playerid=player.playerid) for player in data])).iterator())
    dict_cached_queries['q_player_loans'] = list(DataUsersPlayerloans.objects.for_user(current_user).filter(reduce(lambda x, y: x | y, [Q(playerid=player.playerid) for player in data])).iterator())
    dict_cached_queries['q_edited_player_names'] = list(DataUsersEditedplayernames.objects.for_user(current_user).filter(reduce(lambda x, y: x | y, [Q(playerid=player.playerid) for player in data])).iterator())
    dict_cached_queries['q_teams'] = list(DataUsersTeams.objects.for_user(current_user).filter(reduce(lambda x, y: x | y, [Q(teamid=team.teamid) for team in dict_cached_queries['q_team_player_links']])).iterator())
    dict_cached_queries['q_leagues'] = list(DataUsersLeagues.objects.for_user(current_user).iterator())
    dict_cached_queries['q_league_team_links'] = list(DataUsersLeagueteamlinks.objects.for_user(current_user).filter(reduce(lambda x, y: x | y, [Q(teamid=team.teamid) for team in dict_cached_queries['q_team_player_links']])).iterator())

    # Current date according to in-game calendar
    current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate

    players = list()
    for player in data:
        players.append(FifaPlayer(player, current_user, current_date, dict_cached_queries))

    endtime = time.time() - start # DEBUG
    print ("Loading time: {} Queries: {}".format(endtime, len(connection.queries))) #DEBUG
    return render(request, 'players/players.html', {'players':players})


def player(request, playerid):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "test123"

    data = list(DataUsersPlayers.objects.for_user(current_user).filter(playerid=playerid).select_related('firstname', 'lastname', 'playerjerseyname', 'commonname','nationality',).iterator())
    if len(data) <= 0:
        return render(request, 'players/players.html')

    dict_cached_queries = dict()
    dict_cached_queries['q_team_player_links'] = list(DataUsersTeamplayerlinks.objects.for_user(current_user).filter(reduce(lambda x, y: x | y, [Q(playerid=player.playerid) for player in data])).iterator())
    dict_cached_queries['q_player_loans'] = list(DataUsersPlayerloans.objects.for_user(current_user).filter(reduce(lambda x, y: x | y, [Q(playerid=player.playerid) for player in data])).iterator())
    dict_cached_queries['q_edited_player_names'] = list(DataUsersEditedplayernames.objects.for_user(current_user).filter(reduce(lambda x, y: x | y, [Q(playerid=player.playerid) for player in data])).iterator())
    dict_cached_queries['q_teams'] = list(DataUsersTeams.objects.for_user(current_user).filter(reduce(lambda x, y: x | y, [Q(teamid=team.teamid) for team in dict_cached_queries['q_team_player_links']])).iterator())
    dict_cached_queries['q_leagues'] = list(DataUsersLeagues.objects.for_user(current_user).iterator())
    dict_cached_queries['q_league_team_links'] = list(DataUsersLeagueteamlinks.objects.for_user(current_user).filter(reduce(lambda x, y: x | y, [Q(teamid=team.teamid) for team in dict_cached_queries['q_team_player_links']])).iterator())

    # Current date according to in-game calendar
    current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate

    return render(request, 'players/player.html', {'p':FifaPlayer(data[0], current_user, current_date, dict_cached_queries)})