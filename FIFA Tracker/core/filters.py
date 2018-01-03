from django.db.models import Q
from .fifa_utils import FifaDate
from players.models import DataUsersPlayers, DataUsersTeams, DataUsersTeamplayerlinks

class DataUsersTeamsFilter:
    def __init__(self, for_user, list_teams):
        self.list_teams = list_teams
        self.for_user = for_user

        queryset = DataUsersTeams.objects.for_user(self.for_user).all()
        queryset = self.filter(queryset)
        self.qs = queryset

    def filter(self, queryset):
        value = list(self.list_teams.split(','))
        return queryset.filter(Q(teamid__in=value)) 

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
            gte = range_fields[field] + "__gte" 
            lte = range_fields[field] + "__lte"

            try:
                if (gte in self.request_dict) and (lte in self.request_dict):
                    queryset = queryset.filter(Q((gte, self.request_dict[gte])), Q((lte, self.request_dict[lte])))
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
            if 'age_min' and 'age_max' in self.request_dict:
                birthdate_max = FifaDate().convert_age_to_birthdate(self.current_date, age=self.request_dict['age_min'])
                birthdate_min = FifaDate().convert_age_to_birthdate(self.current_date, age=self.request_dict['age_max']) - 365
                
                queryset = queryset.filter(Q(birthdate__gte=birthdate_min), Q(birthdate__lte=birthdate_max))
        except ValueError:
            pass
        
        return queryset
    
    
    def order(self, queryset):
        return queryset.order_by('-potential')