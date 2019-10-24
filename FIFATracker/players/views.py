from functools import reduce

from django.db.models import Q
from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from core.exceptions import NoResultsError, PrivateProfileError, UnknownError, UserNotExists
from core.generate_view_helper import get_fifaplayers
from core.fifa_utils import PlayerName
from core.session_utils import set_currency, get_current_user, get_fifa_edition, get_career_user
from core.consts import DEFAULT_FIFA_EDITION

from players.models import (
    DataUsersPlayers,
    DataUsersPlayers17,
    DataUsersPlayers19,
    DataUsersPlayers20,
    DataUsersEditedplayernames,
    DataUsersTeams,
    DataUsersLeagues,
    DataNations,
    DataNations17,
    DataNations19,
    DataUsersDcplayernames,
    DataPlayernames,
    DataPlayernames17,
    DataPlayernames19,
)


def ajax_players_by_name(request):
    if request.user.is_authenticated:
        current_user = get_current_user(request)
        fifa_edition = get_fifa_edition(request)
    else:
        current_user = "guest"
        fifa_edition = DEFAULT_FIFA_EDITION

    players_found = list()

    playername = request.GET.get('playername', None)
    if playername and len(playername) > 1:
        playername = playername.split()  # split space
        dict_cached_queries = dict()
        valid_nameids = list()
        query = reduce(lambda x, y: x | y, [
                       Q(name__unaccent__istartswith=name) for name in playername])
        if fifa_edition == 18:
            table_playernames = list(
                DataPlayernames.objects.all().filter(query).iterator())
        else:
            playernames_model = ContentType.objects.get(
                model='dataplayernames{}'.format(fifa_edition)
            ).model_class()
            table_playernames = list(
                playernames_model.objects.all().filter(query).iterator())

        for player in table_playernames:
            if player.nameid in valid_nameids:
                continue
            valid_nameids.append(player.nameid)

        dict_cached_queries['q_dcplayernames'] = list(
            DataUsersDcplayernames.objects.for_user(current_user).all().filter(query).iterator())

        for player in dict_cached_queries['q_dcplayernames']:
            if player.nameid in valid_nameids:
                continue
            valid_nameids.append(player.nameid)

        dict_cached_queries['q_dcplayernames'] = list(
            DataUsersDcplayernames.objects.for_user(current_user).all().iterator())

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

        if fifa_edition == 18:
            players = list(DataUsersPlayers.objects.for_user(current_user).select_related(
                'firstname', 'lastname', 'playerjerseyname', 'commonname',
            ).filter(
                Q(playerid__in=valid_playerids) | Q(firstname_id__in=valid_nameids) |
                Q(lastname_id__in=valid_nameids) | Q(
                    commonname_id__in=valid_nameids)
            ).all().order_by('-overallrating')[:12].iterator())
        else:
            players_model = ContentType.objects.get(model='datausersplayers{}'.format(fifa_edition)).model_class()
            players = list(players_model.objects.for_user(current_user).select_related(
                'firstname', 'lastname', 'playerjerseyname', 'commonname',
            ).filter(
                Q(playerid__in=valid_playerids) | Q(firstname_id__in=valid_nameids) |
                Q(lastname_id__in=valid_nameids) | Q(
                    commonname_id__in=valid_nameids)
            ).all().order_by('-overallrating')[:12].iterator())

        available_positions = ('GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM',
                               'RM', 'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW')

        for player in players:
            p = dict()
            p['playerid'] = player.playerid
            p['overallrating'] = player.overallrating
            p['position'] = available_positions[player.preferredposition1]
            p['playername'] = PlayerName(
                player, dict_cached_queries).playername['knownas']
            players_found.append(p)

    data = {
        'players': players_found,
    }

    return JsonResponse(data)


def ajax_teams(request):
    if request.user.is_authenticated:
        current_user = get_current_user(request)
    else:
        current_user = "guest"

    selected = request.GET.get('selected', None)

    if selected:
        selected = list(selected.split(","))
        teams = list(DataUsersTeams.objects.for_user(
            current_user).all().filter(Q(teamid__in=selected)).values())
    else:
        teams = list(DataUsersTeams.objects.for_user(
            current_user).all().values())

    data = {
        'teams': teams
    }

    return JsonResponse(data)


def ajax_leagues(request):
    if request.user.is_authenticated:
        current_user = get_current_user(request)
    else:
        current_user = "guest"

    selected = request.GET.get('selected', None)

    if selected:
        selected = list(selected.split(","))
        leagues = list(DataUsersLeagues.objects.for_user(
            current_user).all().filter(Q(leagueid__in=selected)).values())
    else:
        leagues = list(DataUsersLeagues.objects.for_user(
            current_user).all().values())

    data = {
        'leagues': leagues,
    }

    return JsonResponse(data)


def ajax_nationality(request):
    if request.user.is_authenticated:
        fifa_edition = get_fifa_edition(request)
    else:
        fifa_edition = DEFAULT_FIFA_EDITION

    if fifa_edition == 18:
        nations_model = ContentType.objects.get(model='datanations').model_class()
    else:
        nations_model = ContentType.objects.get(model='datanations{}'.format(fifa_edition)).model_class()

    selected = request.GET.get('selected', None)
    if selected:
        selected = list(selected.split(","))
        nations = list(nations_model.objects.all().filter(
            Q(nationid__in=selected)).values())
    else:
        nations = list(nations_model.objects.all().values())

    data = {
        'nations': nations,
    }

    return JsonResponse(data)


def players(request):
    try:
        additional_filters = {'gender': 0}
        context = get_fifaplayers(request, additional_filters=additional_filters, paginate=True)
        return render(request, 'players/players.html', context)
    except (NoResultsError, PrivateProfileError, UnknownError, UserNotExists) as e:
        messages.error(request, e)
        return redirect('home')


def player(request, playerid):
    try:
        additional_filters = {'playerid': playerid, 'gender': 0}
        context = get_fifaplayers(
            request, additional_filters=additional_filters, paginate=False)

        return render(
            request, 'players/player.html',
            {'p': context['players'][0], 'fifa_edition': context['fifa_edition']}
        )
    except (NoResultsError, PrivateProfileError, UnknownError, UserNotExists) as e:
        messages.error(request, e)
        return redirect('home')
