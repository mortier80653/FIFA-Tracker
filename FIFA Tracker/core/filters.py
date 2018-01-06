from django.db.models import Q
from .fifa_utils import FifaDate
from players.models import DataUsersPlayers, DataUsersLeagues, DataUsersTeams, DataUsersTeamplayerlinks, DataUsersLeagueteamlinks

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

        return DataUsersTeamsFilter(for_user=self.for_user, list_teams=teams[:-1]).get_player_ids()

class DataUsersTeamsFilter:
    def __init__(self, for_user, list_teams):
        self.list_teams = list_teams
        self.for_user = for_user

        queryset = DataUsersTeams.objects.for_user(self.for_user).all()
        queryset = self.filter(queryset)
        self.qs = queryset

    def filter(self, queryset):
        return queryset.filter(Q(teamid__in=list(self.list_teams.split(',')))) 

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

class DataUsersPlayersFilter:
    def __init__(self, request, for_user, current_date):
        self.request_dict = request.GET.copy()
        self.for_user = for_user
        self.current_date = current_date
        
        queryset = DataUsersPlayers.objects.for_user(self.for_user).select_related('firstname', 'lastname', 'playerjerseyname', 'commonname','nationality',)
        queryset = self.filter(queryset)
        queryset = self.order(queryset)
        self.qs = queryset

    def filter(self, queryset):
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
            if 'isretiring' in self.request_dict:
                queryset = queryset.filter( Q(isretiring=self.request_dict['isretiring']) )
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
                list_playerids = DataUsersTeamsFilter(for_user=self.for_user, list_teams=self.request_dict['teamid']).get_player_ids()
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
            return queryset.order_by(self.request_dict['order_by'])
        else:
            return queryset.order_by('-overallrating')


    def _check_key(self, d, key):
        if key in d:
            return d[key]
        else:
            return None