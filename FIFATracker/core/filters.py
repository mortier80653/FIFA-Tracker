from django.db.models import Q
from .fifa_utils import FifaDate
from players.models import (
    DataUsersPlayers,
    DataUsersPlayers17,
    DataUsersLeagues, 
    DataUsersTeams, 
    DataUsersTeamplayerlinks, 
    DataUsersLeagueteamlinks, 
    DataUsersPlayerloans,
    DataUsersCareerRestReleaseClauses,
)

from core.models import (
    DataUsersCareerTransferOffer,
)

class DataUsersCareerRestReleaseClausesFilter:
    def __init__(self, request, for_user):
        self.request_dict = request
        self.for_user = for_user

        queryset = DataUsersCareerRestReleaseClauses.objects.for_user(self.for_user).all()
        queryset = self.filter(queryset)
        queryset = self.order(queryset)
        self.qs = queryset
        

    def filter(self, queryset):
        try:
            if 'release_clause__gte' in self.request_dict or 'release_clause__lte' in self.request_dict:
                clause_min = int(self._check_key(self.request_dict, 'release_clause__gte') or 1)
                clause_max = int(self._check_key(self.request_dict, 'release_clause__lte') or 999999999)
                
                queryset = queryset.filter(Q(release_clause__gte=clause_min), Q(release_clause__lte=clause_max))
        except ValueError:
            pass

        return queryset

    def order(self, queryset):
        if 'order_by' in self.request_dict:
            valid_fields = [f.name for f in DataUsersCareerRestReleaseClauses._meta.get_fields()]
            orderby = self.request_dict['order_by'].replace('-', "")
            if orderby in valid_fields:
                return queryset.order_by(self.request_dict['order_by'], 'playerid')

        return queryset
        #return queryset.order_by('-release_clause', 'playerid')

    def get_player_ids(self):
        eval_DataUsersCareerRestReleaseClauses_qs = list(self.qs.iterator())
        list_filtered_players = list()

        for player in eval_DataUsersCareerRestReleaseClauses_qs:
            list_filtered_players.append(player.playerid)

        return list_filtered_players

    def _check_key(self, d, key):
        if key in d:
            return d[key]
        else:
            return None

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
                    val_top = (self._check_key(self.request_dict, range_top) or 500000000) 
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

    def _check_key(self, d, key):
        if key in d:
            return d[key]
        else:
            return None


class DataUsersPlayerloansFilter:
    def __init__(self, request, for_user, current_date=18):
        self.request_dict = request
        self.for_user = for_user
        self.current_date = current_date

        queryset = DataUsersPlayerloans.objects.for_user(self.for_user).all()
        queryset = self.filter(queryset)
        self.qs = queryset

    def filter(self, queryset):

        # exclude invalid date
        invalid_dates = FifaDate().convert_to_fifa_date(self.current_date)
        queryset = queryset.exclude(Q(loandateend__lte=invalid_dates))

        '''
        if self.fifa_edition == 17:
            # For some reasons players in FIFA 17 are in 'playerloans' table even if they are not loaned out.
            invalid_dates = [
                158745,     # June  1,  2017
                158775,     # July  1,  2017
                158959,     # January  1,  2018 
                159140,     # July  1,  2018
            ]
            queryset = queryset.exclude(Q(loandateend__in=invalid_dates))  # 
        '''

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
    def __init__(self, request, for_user, current_date=20170701, sort=True, fifa_edition=18):
        self.request_dict = request
        self.for_user = for_user
        self.current_date = current_date
        self.current_date_py = FifaDate().convert_to_py_date(fifa_date=self.current_date)
        self.fifa_edition = fifa_edition
        
        if self.fifa_edition == 18:
            queryset = DataUsersPlayers.objects.for_user(self.for_user).select_related('firstname', 'lastname', 'playerjerseyname', 'commonname', 'nationality',)
        else:
            queryset = DataUsersPlayers17.objects.for_user(self.for_user).select_related('firstname', 'lastname', 'playerjerseyname', 'commonname', 'nationality',)

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
            if 'value_usd__gte' in self.request_dict or 'value_usd__lte' in self.request_dict:
                player_value_usd_min = int(self._check_key(self.request_dict, 'value_usd__gte') or 0)
                player_value_usd_max = int(self._check_key(self.request_dict, 'value_usd__lte') or 500000000)
                
                queryset = queryset.filter(Q(value_usd__gte=player_value_usd_min), Q(value_usd__lte=player_value_usd_max))
        except ValueError:
            pass

        try:
            if 'value_eur__gte' in self.request_dict or 'value_eur__lte' in self.request_dict:
                player_value_eur_min = int(self._check_key(self.request_dict, 'value_eur__gte') or 0)
                player_value_eur_max = int(self._check_key(self.request_dict, 'value_eur__lte') or 500000000)
                
                queryset = queryset.filter(Q(value_eur__gte=player_value_eur_min), Q(value_eur__lte=player_value_eur_max))
        except ValueError:
            pass

        try:
            if 'value_gbp__gte' in self.request_dict or 'value_gbp__lte' in self.request_dict:
                player_value_gbp_min = int(self._check_key(self.request_dict, 'value_gbp__gte') or 0)
                player_value_gbp_max = int(self._check_key(self.request_dict, 'value_gbp__lte') or 500000000)
                
                queryset = queryset.filter(Q(value_gbp__gte=player_value_gbp_min), Q(value_gbp__lte=player_value_gbp_max))
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
                highest_real_playerid = 280000
                if int(self.request_dict['isreal']) == 0:
                    #All regens, pregens etc.
                    queryset = queryset.filter( Q(playerid__gte=highest_real_playerid) )
                elif int(self.request_dict['isreal']) == 1:
                    #Real players that exists since beginning of the career
                    queryset = queryset.filter( Q(playerid__lte=highest_real_playerid) )               
        except ValueError:
            pass
        
        # DataUsersCareerRestReleaseClausesFilter
        player_release_clauses = DataUsersCareerRestReleaseClausesFilter(request=self.request_dict, for_user=self.for_user)
        player_release_clauses_ids = None
        try:
            if 'hasreleaseclause' in self.request_dict and int(self.request_dict['hasreleaseclause']) in range(0,2):
                if player_release_clauses_ids is None:
                    player_release_clauses_ids = player_release_clauses.get_player_ids()
                if int(self.request_dict['hasreleaseclause']) == 0:
                    queryset = queryset.filter(~Q(playerid__in=player_release_clauses_ids))
                elif int(self.request_dict['hasreleaseclause']) == 1:
                    queryset = queryset.filter(Q(playerid__in=player_release_clauses_ids))
        except ValueError:
            pass

        try:
            if 'release_clause__gte' in self.request_dict or 'release_clause__lte' in self.request_dict:
                if player_release_clauses_ids is None:
                    player_release_clauses_ids = player_release_clauses.get_player_ids()

                queryset = queryset.filter(Q(playerid__in=player_release_clauses_ids))
        except ValueError:
            pass
        
        # DataUsersPlayerloansFilter
        player_loans = DataUsersPlayerloansFilter(for_user=self.for_user, request=self.request_dict, current_date=self.current_date)
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

        try:
            if 'contractvaliduntil__gte' in self.request_dict or 'contractvaliduntil__lte' in self.request_dict:
                contractvaliduntil_min = int(self._check_key(self.request_dict, 'contractvaliduntil__gte') or self.current_date_py.year)
                contractvaliduntil_max = int(self._check_key(self.request_dict, 'contractvaliduntil__lte') or self.current_date_py.year + 10)
                
                queryset = queryset.filter(Q(contractvaliduntil__gte=contractvaliduntil_min), Q(contractvaliduntil__lte=contractvaliduntil_max))
        except ValueError:
            pass

        try:
            if 'hashighqualityhead' in self.request_dict and int(self.request_dict['hashighqualityhead']) in range(0,2):
                queryset = queryset.filter( Q(hashighqualityhead=self.request_dict['hashighqualityhead']) )
        except ValueError:
            pass

        try:
            if 'shoetypecode' in self.request_dict:
                value = list(self.request_dict['shoetypecode'].split(','))
                queryset = queryset.filter( Q(shoetypecode__in=value) )
        except ValueError:
            pass

        try:
            if 'skintonecode' in self.request_dict:
                value = list(self.request_dict['skintonecode'].split(','))
                queryset = queryset.filter( Q(skintonecode__in=value) )
        except ValueError:
            pass

        try:
            if 'haircolorcode' in self.request_dict:
                value = list(self.request_dict['haircolorcode'].split(','))
                queryset = queryset.filter( Q(haircolorcode__in=value) )
        except ValueError:
            pass

        try:
            if 'headtype' in self.request_dict:
                value = list(self.request_dict['headtype'].split(','))
                headtypecodes = list()

                for i in value:
                    if i == '0':
                        # Caucasian
                        caucasians = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 5500, 5501, 5502, 5503, 5504, 5505]
                        headtypecodes.extend(caucasians)
                    elif i == '1':
                        # African
                        africans = [1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 3000, 3001, 3002, 3003, 3004, 3005, 4500, 4501, 4502, 4503, 4504, 4505, 4506, 4507, 4508, 4509, 4510, 4511, 4512, 4513, 4514, 4515, 4516, 4517, 4518, 4519, 4520, 4521, 4522, 4523, 4524, 4525, 5000, 5001, 5002, 5003, 6500, 6501, 6502, 8500, 8501, 8502, 10000, 10001, 10002, 10500, 10501, 10502]
                        headtypecodes.extend(africans)
                    elif i == '2':
                        # Latin
                        latins = [1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 7000, 7001, 7002, 7003, 7004, 7005, 7006, 7007, 7008, 7009, 7010, 7011]
                        headtypecodes.extend(latins)
                    elif i == '3':
                        # European
                        europeans = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 3500, 3501, 3502, 3503, 3504, 3505, 4000, 4001, 4002, 4003, 7500, 7501, 7502, 9000, 9001, 9002, 9500, 9501, 9502]
                        headtypecodes.extend(europeans)
                    elif i == '4':
                        # Arabic
                        arabic = [2500, 2501, 2502, 2503, 2504, 2505, 2506, 2507, 2508, 2509, 2510, 2511, 2512, 2513, 2514, 2515, 2516, 2517, 2518, 8000, 8001, 8002]
                        headtypecodes.extend(arabic)
                    elif i == '5':
                        # Asian
                        asian = [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 6000, 6001, 6002, 6003, 6004, 6005, 6006, 6007, 6008, 6009]
                        headtypecodes.extend(asian)
                
                queryset = queryset.filter( Q(headtypecode__in=headtypecodes) )
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