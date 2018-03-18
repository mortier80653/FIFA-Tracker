from django.db.models import Q
from .fifa_utils import FifaDate
from players.models import (
    DataUsersPlayers,
    DataUsersLeagues, 
    DataUsersTeams, 
    DataUsersTeamplayerlinks, 
    DataUsersLeagueteamlinks, 
    DataUsersPlayerloans,
)

from core.models import (
    DataUsersCareerTransferOffer,
)

class DataUsersCareerTransferOfferFilter:
    def __init__(self, request, for_user):
        self.request_dict = request
        self.for_user = for_user

        queryset = DataUsersCareerTransferOffer.objects.for_user(self.for_user).all()
        queryset = self.filter(queryset)
        queryset = self.order(queryset)
        self.qs = queryset

    def filter(self, queryset):
        # bool
        try:
            if 'iscputransfer' in self.request_dict and int(self.request_dict['iscputransfer']) in range(0,2):
                queryset = queryset.filter( Q(iscputransfer=self.request_dict['iscputransfer']) )
        except ValueError:
            pass

        try:
            if 'isloan' in self.request_dict and int(self.request_dict['isloan']) in range(0,2):
                queryset = queryset.filter( Q(isloan=self.request_dict['isloan']) )
        except ValueError:
            pass

        try:
            if 'isloanbuy' in self.request_dict and int(self.request_dict['isloanbuy']) in range(0,2):
                queryset = queryset.filter( Q(isloanbuy=self.request_dict['isloanbuy']) )
        except ValueError:
            pass

        try:
            if 'issnipe' in self.request_dict and int(self.request_dict['issnipe']) in range(0,2):
                queryset = queryset.filter( Q(issnipe=self.request_dict['issnipe']) )
        except ValueError:
            pass

        # Range
        range_fields = [
            'offeredfee',
            'offeredwage',
            'valuation',
        ]

        for field in range(len(range_fields)):
            range_bottom = range_fields[field] + "__gte" 
            range_top = range_fields[field] + "__lte"

            try:
                if range_bottom in self.request_dict or range_top in self.request_dict:
                    val_bottom = (self._check_key(self.request_dict, range_bottom) or 1) 
                    val_top = (self._check_key(self.request_dict, range_top) or 99) 
                    queryset = queryset.filter(
                        Q((range_bottom, val_bottom)), 
                        Q((range_top, val_top)),
                    )
            except ValueError:
                pass

        # Rest
        try:
            if 'fromteamid' in self.request_dict:
                teams_list = self.request_dict['fromteamid']
                queryset = queryset.filter(Q(teamid__in=list(teams_list.split(',')))) 
        except ValueError:
            pass

        try:
            if 'offerteamid' in self.request_dict:
                teams_list = self.request_dict['offerteamid']
                queryset = queryset.filter(Q(offerteamid__in=list(teams_list.split(',')))) 
        except ValueError:
            pass

        try:
            if 'result' in self.request_dict and int(self.request_dict['result']) in range(0,33):
                value = int(self.request_dict['result'])
                queryset = queryset.filter(Q(result=value))
        except ValueError:
            pass

        try:
            if 'stage' in self.request_dict:
                value = self.request_dict['stage']
                queryset = queryset.filter( Q(stage=value) )
        except ValueError:
            pass

        return queryset

    def order(self, queryset):
        if 'order_by' in self.request_dict:
            valid_fields = [f.name for f in DataUsersCareerTransferOffer._meta.get_fields()]
            orderby = self.request_dict['order_by'].replace('-', "")
            if orderby in valid_fields:
                return queryset.order_by(self.request_dict['order_by'], 'offerid')

        return queryset.order_by('-offeredfee', 'offerid')


class DataUsersPlayerloansFilter:
    def __init__(self, request, for_user):
        self.request_dict = request
        self.for_user = for_user

        queryset = DataUsersPlayerloans.objects.for_user(self.for_user).all()
        queryset = self.filter(queryset)
        self.qs = queryset

    def filter(self, queryset):
        try:
            if 'teamidloanedfrom' in self.request_dict:
                value = list(self.request_dict['teamidloanedfrom'].split(','))
                queryset = queryset.filter( Q(teamidloanedfrom__in=value) )
        except ValueError:
            pass

        return queryset

    def get_player_ids(self):
        eval_DataUsersPlayerloans_qs = list(self.qs.iterator())
        list_filtered_players = list()

        for player in eval_DataUsersPlayerloans_qs:
            list_filtered_players.append(player.playerid)

        return list_filtered_players

class DataUsersLeagueteamlinksFilter:
    def __init__(self, request, for_user):
        self.request_dict = request
        self.for_user = for_user

        queryset = DataUsersLeagueteamlinks.objects.for_user(self.for_user).all()
        queryset = self.filter(queryset)
        self.qs = queryset

    def filter(self, queryset):
        try:
            if 'teamtype' in self.request_dict:
                leagueid_nt = [
                    78,     # Men's
                    2136,   # Women's
                ]
                tt = int(self.request_dict['teamtype'])
                if tt == 0:
                    # Club Teams only
                    queryset = queryset.exclude(Q (leagueid__in=leagueid_nt))
                elif tt == 1:
                    # National Teams only
                    queryset = queryset.filter(Q (leagueid__in=leagueid_nt))
        except ValueError:
            pass

        try:
            if 'leagueid' in self.request_dict:
                value = list(self.request_dict['leagueid'].split(','))
                queryset = queryset.filter( Q(leagueid__in=value) )
        except ValueError:
            pass

        return queryset

class DataUsersLeaguesFilter:
    def __init__(self, for_user, list_leagues):
        self.list_leagues = list_leagues
        self.for_user = for_user

        queryset = DataUsersLeagues.objects.for_user(self.for_user).all()
        queryset = self.filter(queryset)
        self.qs = queryset

    def filter(self, queryset):
        return queryset.filter(Q(leagueid__in=list(self.list_leagues.split(',')))) 

    def get_player_ids(self):
        eval_DataUsersLeagues_qs = list(self.qs.iterator())
        list_filtered_leagues = list()

        for league in eval_DataUsersLeagues_qs:
            list_filtered_leagues.append(league.leagueid)

        leagueteamlinks = list(DataUsersLeagueteamlinks.objects.for_user(self.for_user).filter(leagueid__in=list_filtered_leagues).iterator())
        teams = ""

        for team in leagueteamlinks:
            teams = teams + "{},".format(team.teamid)

        return DataUsersTeamsFilter(for_user=self.for_user, request={"teamid": teams[:-1]}).get_player_ids()

class DataUsersTeamsFilter:
    def __init__(self, request, for_user):
        self.request_dict = request
        self.for_user = for_user

        queryset = DataUsersTeams.objects.for_user(self.for_user).all()
        queryset = self.filter(queryset)
        queryset = self.order(queryset)
        self.qs = queryset

    def filter(self, queryset):
        # Exclude women teams
        women_nt = [
            '112998',   # Australia Women
            '112999',   # Brazil Women
            '113000',   # Canada Women
            '113001',   # China PR Women
            '113002',   # England Women
            '113003',   # France Women
            '113004',   # Germany Women
            '113005',   # Italy Women
            '113007',   # Norway Women
            '113008',   # Sweden Women
            '113009',   # United States Women
            '113010',   # Mexico Women
            '113011',   # Holland Women
            '113012',   # Spain Women
            '113258',   # New Zealand Women
        ]
        queryset = queryset.exclude(Q(teamid__in=women_nt))

        # DataUsersLeagueteamlinksFilter
        try:
            leagueteamsfilter = list(DataUsersLeagueteamlinksFilter(request=self.request_dict, for_user=self.for_user).qs.iterator())
            leagueteamsfilter_teamids = list()
            for team in leagueteamsfilter:
                leagueteamsfilter_teamids.append(team.teamid)
                
            queryset = queryset.filter(Q(teamid__in=leagueteamsfilter_teamids))
        except ValueError:
            pass

        range_fields = [
            'overallrating',
            'attackrating',
            'midfieldrating',
            'defenserating',
            'transferbudget',
            'clubworth',
            'popularity',
            'domesticprestige',
            'internationalprestige',
            'leaguetitles',
            'domesticcups',
            'youthdevelopment',
        ]

        for field in range(len(range_fields)):
            range_bottom = range_fields[field] + "__gte" 
            range_top = range_fields[field] + "__lte"

            try:
                if range_bottom in self.request_dict or range_top in self.request_dict:
                    val_bottom = (self._check_key(self.request_dict, range_bottom) or 0) 
                    val_top = (self._check_key(self.request_dict, range_top) or 500000000) 
                    queryset = queryset.filter(
                        Q((range_bottom, val_bottom)), 
                        Q((range_top, val_top)),
                    )
            except ValueError:
                pass

        try:
            if 'teamid' in self.request_dict:
                teams_list = self.request_dict['teamid']
                queryset = queryset.filter(Q(teamid__in=list(teams_list.split(',')))) 
        except ValueError:
            pass

        return queryset

    def order(self, queryset):
        if 'order_by' in self.request_dict:
            valid_fields = [f.name for f in DataUsersTeams._meta.get_fields()]
            orderby = self.request_dict['order_by'].replace('-', "")
            if orderby in valid_fields:
                return queryset.order_by(self.request_dict['order_by'], 'teamid')

        return queryset.order_by('-overallrating', 'teamid')

    def get_player_ids(self):
        eval_DataUsersTeams_qs = list(self.qs.iterator())
        list_filtered_teams = list()
        for team in eval_DataUsersTeams_qs:
            list_filtered_teams.append(team.teamid)

        teamplayerlinks = list(DataUsersTeamplayerlinks.objects.for_user(self.for_user).filter(teamid__in=list_filtered_teams).iterator())
        list_players = list()

        for player in teamplayerlinks:
            list_players.append(player.playerid)

        return list_players

    def _check_key(self, d, key):
        if key in d:
            return d[key]
        else:
            return None

class DataUsersPlayersFilter:
    def __init__(self, request, for_user, current_date=20170701, sort=True):
        self.request_dict = request
        self.for_user = for_user
        self.current_date = current_date
        
        queryset = DataUsersPlayers.objects.for_user(self.for_user).select_related('firstname', 'lastname', 'playerjerseyname', 'commonname', 'nationality',)
        queryset = self.filter(queryset)
        if sort:
            queryset = self.order(queryset)

        self.qs = queryset

    def filter(self, queryset):
        try:
            if 'playerid' in self.request_dict:
                value = list(self.request_dict['playerid'].split(','))
                queryset = queryset.filter( Q(playerid__in=value) )
        except ValueError:
            pass

        range_fields = [
            'overallrating',
            'potential',
            'weakfootabilitytypecode',
            'internationalrep',
            'height',
            'weight',
            'crossing',
            'finishing',
            'headingaccuracy',
            'shortpassing',
            'volleys',
            'marking',
            'standingtackle',
            'slidingtackle',
            'dribbling',
            'curve',
            'freekickaccuracy',
            'longpassing',
            'ballcontrol',
            'shotpower',
            'jumping',
            'stamina',
            'strength',
            'longshots',
            'acceleration',
            'sprintspeed',
            'agility',
            'reactions',
            'balance',
            'aggression',
            'composure',
            'interceptions',
            'positioning',
            'vision',
            'penalties',
            'gkdiving',
            'gkhandling',
            'gkkicking',
            'gkpositioning',
            'gkreflexes',
        ]

        for field in range(len(range_fields)):
            range_bottom = range_fields[field] + "__gte" 
            range_top = range_fields[field] + "__lte"

            try:
                if range_bottom in self.request_dict or range_top in self.request_dict:
                    val_bottom = (self._check_key(self.request_dict, range_bottom) or 1) 
                    val_top = (self._check_key(self.request_dict, range_top) or 99) 
                    queryset = queryset.filter(
                        Q((range_bottom, val_bottom)), 
                        Q((range_top, val_top)),
                    )
            except ValueError:
                pass

        try:
            if 'skillmoves__gte' in self.request_dict or 'skillmoves__lte' in self.request_dict:
                sm_min = int(self._check_key(self.request_dict, 'skillmoves__gte') or 1) - 1
                sm_max = int(self._check_key(self.request_dict, 'skillmoves__lte') or 5) - 1
                
                queryset = queryset.filter(Q(skillmoves__gte=sm_min), Q(skillmoves__lte=sm_max))
        except ValueError:
            pass
    
        try:
            if 'attackingworkrate' in self.request_dict:
                value = list(self.request_dict['attackingworkrate'].split(','))
                queryset = queryset.filter( Q(attackingworkrate__in=value) )
        except ValueError:
            pass

        try:
            if 'defensiveworkrate' in self.request_dict:
                value = list(self.request_dict['defensiveworkrate'].split(','))
                queryset = queryset.filter( Q(defensiveworkrate__in=value) )
        except ValueError:
            pass

        try:
            if 'isretiring' in self.request_dict and int(self.request_dict['isretiring']) in range(0,2):
                queryset = queryset.filter( Q(isretiring=self.request_dict['isretiring']) )
        except ValueError:
            pass

        try:
            if 'isreal' in self.request_dict and int(self.request_dict['isreal']) in range(0,2):
                highest_real_playerid = 240895
                if int(self.request_dict['isreal']) == 0:
                    #All regens, pregens etc.
                    queryset = queryset.filter( Q(playerid__gte=highest_real_playerid) )
                elif int(self.request_dict['isreal']) == 1:
                    #Real players that exists since beginning of the career
                    queryset = queryset.filter( Q(playerid__lte=highest_real_playerid) )               
        except ValueError:
            pass

        # DataUsersPlayerloansFilter
        player_loans = DataUsersPlayerloansFilter(for_user=self.for_user, request=self.request_dict)
        player_loans_ids = None
        try:
            if 'teamidloanedfrom' in self.request_dict:
                if player_loans_ids is None:
                    player_loans_ids = player_loans.get_player_ids()

        except ValueError:
            pass
        
        try:
            if 'isonloan' in self.request_dict and int(self.request_dict['isonloan']) in range(0,2):
                if player_loans_ids is None:
                    player_loans_ids = player_loans.get_player_ids()

                if int(self.request_dict['isonloan']) == 0:
                    # Players is not on loan.
                    queryset = queryset.filter(~Q(playerid__in=player_loans_ids))
                elif int(self.request_dict['isonloan']) == 1:
                    # Player is currently on loan.
                    
                    queryset = queryset.filter(Q(playerid__in=player_loans_ids))
        except ValueError:
            pass

        try:
            if 'leagueid' in self.request_dict:
                list_playerids = DataUsersLeaguesFilter(for_user=self.for_user, list_leagues=self.request_dict['leagueid']).get_player_ids()
                queryset = queryset.filter(Q(playerid__in=list_playerids))
        except ValueError:
            pass

        try:
            if 'teamid' in self.request_dict:
                req_dict = self.request_dict
                if 'overallrating__gte' in req_dict:
                    del req_dict['overallrating__gte']

                if 'overallrating__lte' in req_dict:
                    del req_dict['overallrating__lte']

                list_playerids = DataUsersTeamsFilter(for_user=self.for_user, request=req_dict).get_player_ids()
                if player_loans_ids:
                    list_playerids.extend(player_loans_ids)
                queryset = queryset.filter(Q(playerid__in=list_playerids))

        except ValueError:
            pass

        try:
            if 'preferredpositions' in self.request_dict:
                value = list(self.request_dict['preferredpositions'].split(','))
                queryset = queryset.filter(
                    Q(preferredposition1__in=value) | Q(preferredposition2__in=value) | Q(preferredposition3__in=value) | Q(preferredposition4__in=value)
                )
        except ValueError:
            pass

        try:
            if 'nationalityid' in self.request_dict:
                value = list(self.request_dict['nationalityid'].split(','))
                
                queryset = queryset.filter( Q(nationality__in=value) )
        except ValueError:
            pass

        try:
            if 'age_min' in self.request_dict or 'age_max' in self.request_dict:
                age_min = (self._check_key(self.request_dict, 'age_min') or 1)
                age_max = (self._check_key(self.request_dict, 'age_max') or 99)

                birthdate_max = FifaDate().convert_age_to_birthdate(self.current_date, age=age_min)
                birthdate_min = FifaDate().convert_age_to_birthdate(self.current_date, age=age_max) - 365
                
                queryset = queryset.filter(Q(birthdate__gte=birthdate_min), Q(birthdate__lte=birthdate_max))
        except ValueError:
            pass
        
        return queryset
    
    
    def order(self, queryset):
        if 'order_by' in self.request_dict:
            valid_fields = [f.name for f in DataUsersPlayers._meta.get_fields()]
            orderby = self.request_dict['order_by'].replace('-', "")
            if orderby in valid_fields:
                return queryset.order_by(self.request_dict['order_by'], 'playerid')

        return queryset.order_by('-overallrating', 'playerid')


    def _check_key(self, d, key):
        if key in d:
            return d[key]
        else:
            return None