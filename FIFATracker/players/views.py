from functools import reduce

from django.db.models import Q
from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User

from core.filters import DataUsersPlayersFilter
from core.fifa_utils import FifaPlayer, PlayerName

from .models import (
    DataUsersPlayers, 
    DataUsersTeamplayerlinks, 
    DataUsersPlayerloans, 
    DataUsersEditedplayernames, 
    DataUsersTeams, 
    DataUsersLeagueteamlinks,
    DataUsersCareerCalendar, 
    DataUsersLeagues, 
    DataNations, 
    DataUsersDcplayernames,
    DataPlayernames,
)

from .paginator import MyPaginator

def ajax_players_by_name(request):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "guest"

    players_found = list()

    playername = request.GET.get('playername', None)
    if playername and len(playername) > 1:
        playername = playername.split() # split space
        dict_cached_queries = dict()
        valid_nameids = list()
        query = reduce(lambda x, y: x | y, [Q(name__unaccent__istartswith=name) for name in playername])
        table_playernames = list(DataPlayernames.objects.all().filter(query).iterator())

        for player in table_playernames:
            if player.nameid in valid_nameids:
                continue
            valid_nameids.append(player.nameid)
        
        dict_cached_queries['q_dcplayernames'] = list(DataUsersDcplayernames.objects.for_user(current_user).all().filter(query).iterator())

        for player in dict_cached_queries['q_dcplayernames']:
            if player.nameid in valid_nameids:
                continue
            valid_nameids.append(player.nameid)

        dict_cached_queries['q_dcplayernames'] = list(DataUsersDcplayernames.objects.for_user(current_user).all().iterator())

        valid_playerids = list()
        query_fn = Q()
        query_sn = Q()
        query_cn = Q()

        for name in playername:
            query_fn.add(Q(firstname__unaccent__istartswith=name), Q.OR)
            query_sn.add(Q(surname__unaccent__istartswith=name), Q.OR)
            query_cn.add(Q(commonname__unaccent__istartswith=name), Q.OR)

        dict_cached_queries['q_edited_player_names'] = list(DataUsersEditedplayernames.objects.for_user(current_user).all().filter(
            query_fn | query_sn | query_cn
            ).iterator())

        for player in dict_cached_queries['q_edited_player_names']:
            if player.playerid in valid_playerids:
                continue
            valid_playerids.append(player.playerid)

        players = list(DataUsersPlayers.objects.for_user(current_user).select_related(
                'firstname', 'lastname', 'playerjerseyname', 'commonname',
                ).filter(
                    Q (playerid__in=valid_playerids) | Q (firstname_id__in=valid_nameids) | 
                    Q (lastname_id__in=valid_nameids) | Q(commonname_id__in=valid_nameids)
                ).all().order_by('-overallrating')[:12].iterator())

        available_positions = ('GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM', 'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW')

        for player in players:
            p = dict()
            p['playerid'] = player.playerid
            p['overallrating'] = player.overallrating
            p['position'] = available_positions[player.preferredposition1]
            p['playername'] = PlayerName(player, dict_cached_queries).playername['knownas']
            players_found.append(p)

    data = {
        'players': players_found,
    }

    return JsonResponse(data)

def ajax_teams(request):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "guest"

    selected = request.GET.get('selected', None)

    if selected:
        selected = list(selected.split(","))
        teams = list(DataUsersTeams.objects.for_user(current_user).all().filter(Q(teamid__in=selected)).values())
    else:
        teams = list(DataUsersTeams.objects.for_user(current_user).all().values())

    data = {
        'teams': teams
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

def ajax_nationality(request):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "guest"
        
    selected = request.GET.get('selected', None)
    if selected:
        selected = list(selected.split(","))
        nations = list(DataNations.objects.all().filter(Q(nationid__in=selected)).values())
    else:
        nations = list(DataNations.objects.all().values())

    data = {
        'nations': nations,
    }
    
    return JsonResponse(data)

def players(request):
    request_query_dict = request.GET.copy()

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
        messages.error(request, "Your career file hasn't been processed yet. Displaying default FIFA database data.")
        current_user = "guest"
        current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate

    player_filter = DataUsersPlayersFilter(request_query_dict, for_user=current_user, current_date=current_date)

    paginator = MyPaginator(player_filter.qs.count(), request=request_query_dict, max_per_page=50)

    data = list(player_filter.qs[paginator.results_bottom:paginator.results_top].iterator())

    if len(data) <= 0:
        messages.error(request, 'No results found. Try to change your filters.')
        return redirect('players')

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

    return render(request, 'players/players.html', {'players':players_list, 'paginator':paginator, 'request_query_dict': request_query_dict, })


def player(request, playerid):
    currency_symbols = ('$', '€', '£')
    if request.session.get('currency', None) is None:
        try:
            request.session['currency'] = request.user.profile.currency
        except:
            request.session['currency'] = 1
            
    if request.session.get('currency_symbol', None) is None:
        request.session['currency_symbol'] = currency_symbols[int(request.session['currency'])]

    if 'owner' in request.GET:
        owner = request.GET['owner']
        try:
            is_profile_public = User.objects.get(username=owner).profile.is_public
        except:
            messages.error(request, "Something went wrong... :(")
            return redirect('home')

        if not is_profile_public:
            messages.error(request, "Sorry, you don't have access to see {}'s players. His profile is private. Profile visibility can be changed in Control Panel.".format(owner))
            return redirect('home')
        
        current_user = owner
    elif request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "guest"
        

    # Current date according to in-game calendar
    try:
        current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate
    except IndexError:
        messages.error(request, "Your career file hasn't been processed yet. Displaying default FIFA database data.")
        current_user = "guest"
        current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate

    data = list(DataUsersPlayers.objects.for_user(current_user).filter(playerid=playerid).select_related('firstname', 'lastname', 'playerjerseyname', 'commonname','nationality',).iterator())
    if len(data) <= 0:
        messages.error(request, 'Invalid player id ({})'.format(playerid))
        return redirect('players')

    if 'owner' in request.GET and current_user == owner:
        messages.success(request, "User {} shared this player with you!".format(owner))

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