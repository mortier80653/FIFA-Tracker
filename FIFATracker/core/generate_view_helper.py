from functools import reduce

from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.db import connection
from django.utils.translation import ugettext_lazy as _

from core.exceptions import NoResultsError, PrivateProfileError, UnknownError
from core.fifa_utils import FifaPlayer
from core.paginator import MyPaginator
from core.filters import DataUsersPlayersFilter, DataUsersTeamsFilter, DataUsersCareerTransferOfferFilter

from players.models import (
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
    DataUsersManager,
    DataUsersCareerUsers,
)

from core.models import (
    DataUsersCareerTransferOffer,
)

def set_currency(request):
    # Set Currency
    currency_symbols = ('$', '€', '£')
    if request.session.get('currency', None) is None:
        try:
            request.session['currency'] = request.user.profile.currency
        except:
            request.session['currency'] = 1
            
    if request.session.get('currency_symbol', None) is None:
        request.session['currency_symbol'] = currency_symbols[int(request.session['currency'])]

def get_current_user(request):
    # Set current User
    if 'owner' in request.GET:
        owner = request.GET['owner']
        try:
            user = User.objects.get(username=owner)
            is_profile_public = user.profile.is_public
            fifa_edition = user.profile.fifa_edition
        except Exception as e:
            raise UnknownError(e)

        if not is_profile_public:
            raise PrivateProfileError(_("Sorry, {}'s profile is private. Profile visibility can be changed in Control Panel.").format(owner))
        
        current_user = owner
    elif request.user.is_authenticated:
        current_user = request.user
        fifa_edition = request.user.profile.fifa_edition
    else:
        current_user = "guest"
        fifa_edition = 18

    return current_user, int(fifa_edition)

# Transfers

def transfer_info(playerid, data):
    for transfer in data:
        if int(transfer.playerid) == int(playerid):
            return {
                "playerid": transfer.playerid,
                "offerid": transfer.offerid,
                "snipedteamid": transfer.snipedteamid,
                "offeredcontracttype": transfer.offeredcontracttype,
                "precontract": transfer.precontract,
                "desiredfee": transfer.desiredfee,
                "offeredbonus": transfer.offeredbonus,
                "startdate": transfer.startdate,
                "squadrole": transfer.squadrole,
                "transferwindow": transfer.transferwindow,
                "currentcontractlength": transfer.currentcontractlength,
                "counteroffers": transfer.counteroffers,
                "date": transfer.date,
                "from_team": transfer.teamid,
                "to_team":  transfer.offerteamid,
                "valuation": "{:,}".format(transfer.valuation),
                "offeredfee": "{:,}".format(transfer.offeredfee),
                "offeredwage": "{:,}".format(transfer.offeredwage),
                "exchangeplayerid": transfer.exchangeplayerid,
                "iscputransfer": transfer.iscputransfer,
                "isloan": transfer.isloan,
                "isloanbuy": transfer.isloanbuy,
                "issnipe": transfer.issnipe,
                "stage": transfer.stage,
                "result": transfer.result,
                "approachreason": transfer.approachreason,
            }
        
    return None

def get_transfers(request, additional_filters=None, paginate=False):
    request_query_dict = request.GET.copy()

    current_user, fifa_edition = get_current_user(request)

    if additional_filters:
        for k, v in additional_filters.items():
            request_query_dict[k] = str(v)

    transfer_offer_filter = DataUsersCareerTransferOfferFilter(request_query_dict, for_user=current_user)

    # Paginate results if needed
    if paginate:
        max_per_page = int(request.GET.get('max_per_page', 50))
        if not 25 <= max_per_page <= 100:
            max_per_page = 50
        paginator = MyPaginator(transfer_offer_filter.qs.count(), request=request_query_dict, max_per_page=max_per_page)

        data = list(transfer_offer_filter.qs[paginator.results_bottom:paginator.results_top].iterator())
    else:
        paginator = None
        data = list(transfer_offer_filter.qs.iterator())

    if len(data) <= 0:
        raise NoResultsError(_('No results found. Try to change your filters'))

    playerids = ",".join(str(transfer.playerid) for transfer in data)

    additional_filters = {'playerid': playerids, }
    try:
        context_data = get_fifaplayers(request, additional_filters=additional_filters, paginate=False, sort=False)
    except (NoResultsError):
        context_data = dict()
        context_data['players'] = None

    if context_data['players']:
        # keep order from 'transfer_offer_filter'
        players_original_order = list()

        copy_context_data_players = context_data['players'][:]
        for playerid in playerids.split(','):
            for p in copy_context_data_players:
                if int(playerid) == int(p.player.playerid):
                    t_info = transfer_info(playerid, data)
                    if t_info:
                        setattr(p, 'transfer_info', t_info)
                    players_original_order.append(p)
    
        context_data['players'] = players_original_order 

    
    context_data['paginator'] = paginator
    return context_data


# Teams
def get_team(request, teamid=0, additional_filters=None):
    request_query_dict = request.GET.copy()

    set_currency(request)
    current_user, fifa_edition = get_current_user(request)

    #additional_filters = {'teamid': teamid, }
    additional_filters = {'teamid': teamid, 'teamidloanedfrom': teamid, }
    try:
        context_data = get_fifaplayers(request, additional_filters=additional_filters, paginate=False)
    except (NoResultsError):
        context_data = dict()
        context_data['dict_cached_queries'] = dict()
        context_data['players'] = None
        context_data['dict_cached_queries']['q_teams'] = list(DataUsersTeams.objects.for_user(current_user).filter(teamid=teamid).iterator())
        context_data['dict_cached_queries']['q_league_team_links'] = list(DataUsersLeagueteamlinks.objects.for_user(current_user).filter(teamid=teamid).iterator())
        context_data['dict_cached_queries']['q_leagues'] = list(DataUsersLeagues.objects.for_user(current_user).all().iterator())

    if context_data['players']:
        players = context_data['players'][:]
    else:
        players = None

    
    if not context_data['dict_cached_queries']['q_teams']:
        raise NoResultsError(_('No results found. Try to change your filters'))

    # get valid team
    for team in context_data['dict_cached_queries']['q_teams']:
        if int(team.teamid) == int(teamid):
            valid_team = team
            break

    # get valid leagueteamlink
    for ltlink in context_data['dict_cached_queries']['q_league_team_links']:
        if int(ltlink.teamid) == int(teamid):
            valid_ltlink = ltlink
            break

    # get valid league
    for league in context_data['dict_cached_queries']['q_leagues']:
        if int(league.leagueid) == int(valid_ltlink.leagueid):
            valid_league = league
            break

    # manager
    try:
        manager = list(DataUsersManager.objects.for_user(current_user).filter(teamid=teamid).iterator())[0]
        if manager.firstname is None and manager.surname is None:
            manager.firstname = valid_team.teamname
            manager.surname = "Manager"
        elif manager.firstname is None:
            manager.firstname = ""
        elif manager.surname is None:
            manager.surname = ""
    except IndexError:
        manager = {
            'firstname': valid_team.teamname,
            'surname': "Manager",
            'headid': "None",
        }


    # group players
    is_club_team = True
    is_national_team = False
    if players:
        try:                
            if int(players[0].player_teams['national_team']['team']['teamid']) == int(teamid):
                is_national_team = True
                is_club_team = False
        except KeyError:
            pass

        grouped_players = dict()
        grouped_players['GK'] = list()
        grouped_players['DEF'] = list()
        grouped_players['MID'] = list()
        grouped_players['ATT'] = list()
        grouped_players['LOANED_OUT'] = list()
        grouped_players['total_players'] = len(players)

        grouped_players['value_GK'] = 0
        grouped_players['value_DEF'] = 0
        grouped_players['value_MID'] = 0
        grouped_players['value_ATT'] = 0
        grouped_players['value_LOANED_OUT'] = 0   
        grouped_players['total_team_value'] = 0 

        for p in players:
            grouped_players['total_team_value'] += p.player_value.value
            if int(p.player_contract['isloanedout']) == 1 and int(p.player_contract['loanedto_clubid']) != int(teamid):
                grouped_players['value_LOANED_OUT'] += p.player_value.value
                grouped_players['LOANED_OUT'].append(p)
                p_index = context_data['players'].index(p)
                del context_data['players'][p_index]
                continue

            if p.player.preferredposition1 == 0:
                grouped_players['value_GK'] += p.player_value.value
                grouped_players['GK'].append(p)
            elif 1 <= p.player.preferredposition1 <= 8:
                grouped_players['value_DEF'] += p.player_value.value
                grouped_players['DEF'].append(p)
            elif 9 <= p.player.preferredposition1 <= 19:
                grouped_players['value_MID'] += p.player_value.value
                grouped_players['MID'].append(p)
            elif 20 <= p.player.preferredposition1 <= 27:
                grouped_players['value_ATT'] += p.player_value.value
                grouped_players['ATT'].append(p)

        grouped_players['total_GK'] = len(grouped_players['GK'])
        grouped_players['total_DEF'] = len(grouped_players['DEF'])
        grouped_players['total_MID'] = len(grouped_players['MID'])
        grouped_players['total_ATT'] = len(grouped_players['ATT'])
    else:
        grouped_players = None

    # print("Queries: {}".format(len(connection.queries)))
    total_careers = len(list(DataUsersCareerUsers.objects.all().filter(Q(clubteamid=teamid) | Q(nationalteamid=teamid)).iterator()))
    
    context = {
        'team': valid_team, 
        'leagueteamlink': valid_ltlink, 
        'league': valid_league,
        'players': context_data['players'],
        'grouped_players': grouped_players,
        'manager': manager,
        'is_club_team': is_club_team,
        'is_national_team': is_national_team,
        'total_careers': total_careers, 
    }

    return context

def get_teams(request, additional_filters=None, paginate=False):
    request_query_dict = request.GET.copy()

    set_currency(request)
    current_user, fifa_edition = get_current_user(request)

    # Apply filters
    if additional_filters:
        for k, v in additional_filters.items():
            request_query_dict[k] = str(v)

    teams_filter = DataUsersTeamsFilter(request_query_dict, for_user=current_user)

    # Paginate results if needed
    if paginate:
        max_per_page = int(request.GET.get('max_per_page', 50))
        if not 25 <= max_per_page <= 100:
            max_per_page = 50
        paginator = MyPaginator(teams_filter.qs.count(), request=request_query_dict, max_per_page=max_per_page)
        data = list(teams_filter.qs[paginator.results_bottom:paginator.results_top].iterator())
    else:
        paginator = None
        data = list(teams_filter.qs.iterator())

    if len(data) <= 0:
        raise NoResultsError(_('No results found. Try to change your filters'))

    dict_cached_queries = dict()
    dict_cached_queries['q_league_team_links'] = list(DataUsersLeagueteamlinks.objects.for_user(current_user).iterator())
    dict_cached_queries['q_leagues'] = list(DataUsersLeagues.objects.for_user(current_user).iterator())

    context = {'teams': data, 'paginator':paginator, 'request_query_dict': request_query_dict, 'dict_cached_queries': dict_cached_queries,}
    return context


# Players
def get_fifaplayers(request, additional_filters=None, paginate=False, sort=True):
    request_query_dict = request.GET.copy()

    set_currency(request)
    current_user, fifa_edition = get_current_user(request)

    # Current date according to in-game calendar
    try:
        current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate
    except IndexError:
        messages.error(request, _("Your career file hasn't been processed yet. Displaying default FIFA database data."))
        current_user = "guest"
        current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate

    # Apply filters
    if additional_filters:
        for k, v in additional_filters.items():
            request_query_dict[k] = str(v)

    player_filter = DataUsersPlayersFilter(request_query_dict, for_user=current_user, current_date=current_date, sort=sort, fifa_edition=fifa_edition)

    # Paginate results if needed
    if paginate:
        max_per_page = int(request.GET.get('max_per_page', 50))
        if not 25 <= max_per_page <= 100:
            max_per_page = 50
        paginator = MyPaginator(player_filter.qs.count(), request=request_query_dict, max_per_page=max_per_page)
        data = list(player_filter.qs[paginator.results_bottom:paginator.results_top].iterator())
    else:
        paginator = None
        data = list(player_filter.qs.iterator())

    if len(data) <= 0:
        raise NoResultsError(_('No results found. Try to change your filters'))

    dict_cached_queries = dict()
    
    dict_cached_queries['q_leagues'] = list(DataUsersLeagues.objects.for_user(current_user).all().iterator())
    dict_cached_queries['q_dcplayernames'] = list(DataUsersDcplayernames.objects.for_user(current_user).all().iterator())
    
    f_playerid = reduce(lambda x, y: x | y, [Q(playerid=player.playerid) for player in data])

    dict_cached_queries['q_team_player_links'] = list(DataUsersTeamplayerlinks.objects.for_user(current_user).filter(f_playerid).iterator())
    dict_cached_queries['q_player_loans'] = list(DataUsersPlayerloans.objects.for_user(current_user).filter(f_playerid).iterator())
    dict_cached_queries['q_edited_player_names'] = list(DataUsersEditedplayernames.objects.for_user(current_user).filter(f_playerid).iterator())

    f_teamid = Q()
    for team in dict_cached_queries['q_team_player_links']:
        f_teamid.add(Q(teamid=team.teamid), Q.OR)

    if len(dict_cached_queries['q_player_loans']) > 0:
        for team in dict_cached_queries['q_player_loans']:
            f_teamid.add(Q(teamid=team.teamidloanedfrom), Q.OR)

    dict_cached_queries['q_teams'] = list(DataUsersTeams.objects.for_user(current_user).filter(f_teamid).iterator())
    dict_cached_queries['q_league_team_links'] = list(DataUsersLeagueteamlinks.objects.for_user(current_user).filter(f_teamid).iterator())

    players_list = list()
    for player in data:
        fp = FifaPlayer(player, current_user, current_date, dict_cached_queries, request.session, fifa_edition)
        players_list.append(fp)

    context = {'players':players_list, 'paginator':paginator, 'request_query_dict': request_query_dict, 'dict_cached_queries': dict_cached_queries,}
    return context