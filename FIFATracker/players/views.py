from functools import reduce

from django.db.models import Q
from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse

from core.filters import DataUsersPlayersFilter
from core.fifa_utils import FifaPlayer

from .models import DataUsersPlayers, DataUsersTeamplayerlinks, DataUsersPlayerloans, DataUsersEditedplayernames, DataUsersTeams
from .models import DataUsersLeagueteamlinks, DataUsersCareerCalendar, DataUsersLeagues, DataNations, DataUsersDcplayernames

from .paginator import MyPaginator


def ajax_teams(request):
    current_user = request.GET.get('username', None)

    data = {
        'teams': list(DataUsersTeams.objects.for_user(current_user).all().values())
    }

    return JsonResponse(data)

def ajax_leagues(request):
    current_user = request.GET.get('username', None)

    data = {
        'leagues': list(DataUsersLeagues.objects.for_user(current_user).all().values())
    }

    return JsonResponse(data)

def ajax_nationality(request):
    data = {
        'nations': list(DataNations.objects.all().values())
    }
    
    return JsonResponse(data)

def players(request):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "guest"

    currency_symbols = ('$', '€', '£')
    if request.session.get('currency', None) is None:
        try:
            request.session['currency'] = request.user.profile.currency
        except:
            request.session['currency'] = 1

    if request.session.get('currency_symbol', None) is None:
        request.session['currency_symbol'] = currency_symbols[int(request.session['currency'])]

    # Current date according to in-game calendar
    try:
        current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate
    except IndexError:
        current_user = "guest"
        current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate

    player_filter = DataUsersPlayersFilter(request, for_user=current_user, current_date=current_date)

    paginator = MyPaginator(player_filter.qs.count(), request=request.GET.copy(), max_per_page=50)

    data = list(player_filter.qs[paginator.results_bottom:paginator.results_top].iterator())

    if len(data) <= 0:
        return render(request, 'players/players.html')

    dict_cached_queries = dict()
    dict_cached_queries['q_leagues'] = list(DataUsersLeagues.objects.for_user(current_user).all().iterator())
    dict_cached_queries['q_dcplayernames'] = list(DataUsersDcplayernames.objects.for_user(current_user).all().iterator())
    
    f_playerid = reduce(lambda x, y: x | y, [Q(playerid=player.playerid) for player in data])

    dict_cached_queries['q_team_player_links'] = list(DataUsersTeamplayerlinks.objects.for_user(current_user).filter(f_playerid).iterator())
    dict_cached_queries['q_player_loans'] = list(DataUsersPlayerloans.objects.for_user(current_user).filter(f_playerid).iterator())
    dict_cached_queries['q_edited_player_names'] = list(DataUsersEditedplayernames.objects.for_user(current_user).filter(f_playerid).iterator())

    f_teamid = reduce(lambda x, y: x | y, [Q(teamid=team.teamid) for team in dict_cached_queries['q_team_player_links']])

    dict_cached_queries['q_teams'] = list(DataUsersTeams.objects.for_user(current_user).filter(f_teamid).iterator())
    dict_cached_queries['q_league_team_links'] = list(DataUsersLeagueteamlinks.objects.for_user(current_user).filter(f_teamid).iterator())

    players_list = list()
    for player in data:
        players_list.append(FifaPlayer(player, current_user, current_date, dict_cached_queries, request.session))

    return render(request, 'players/players.html', {'players':players_list, 'paginator':paginator, 'request_query_dict': request.GET, })


def player(request, playerid):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "guest"

    currency_symbols = ('$', '€', '£')
    if request.session.get('currency', None) is None:
        try:
            request.session['currency'] = request.user.profile.currency
        except:
            request.session['currency'] = 1
            
    if request.session.get('currency_symbol', None) is None:
        request.session['currency_symbol'] = currency_symbols[int(request.session['currency'])]

    # Current date according to in-game calendar
    try:
        current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate
    except IndexError:
        current_user = "guest"
        current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate

    data = list(DataUsersPlayers.objects.for_user(current_user).filter(playerid=playerid).select_related('firstname', 'lastname', 'playerjerseyname', 'commonname','nationality',).iterator())
    if len(data) <= 0:
        return render(request, 'players/players.html')


    dict_cached_queries = dict()

    dict_cached_queries['q_leagues'] = list(DataUsersLeagues.objects.for_user(current_user).all().iterator())
    dict_cached_queries['q_dcplayernames'] = list(DataUsersDcplayernames.objects.for_user(current_user).all().iterator())

    dict_cached_queries['q_team_player_links'] = list(DataUsersTeamplayerlinks.objects.for_user(current_user).filter(playerid=playerid).iterator())
    dict_cached_queries['q_player_loans'] = list(DataUsersPlayerloans.objects.for_user(current_user).filter(playerid=playerid).iterator())
    dict_cached_queries['q_edited_player_names'] = list(DataUsersEditedplayernames.objects.for_user(current_user).filter(playerid=playerid).iterator())

    f_teamid = reduce(lambda x, y: x | y, [Q(teamid=team.teamid) for team in dict_cached_queries['q_team_player_links']])

    dict_cached_queries['q_teams'] = list(DataUsersTeams.objects.for_user(current_user).filter(f_teamid).iterator())
    dict_cached_queries['q_league_team_links'] = list(DataUsersLeagueteamlinks.objects.for_user(current_user).filter(f_teamid).iterator())

    return render(request, 'players/player.html', {'p':FifaPlayer(data[0], current_user, current_date, dict_cached_queries, request.session)})