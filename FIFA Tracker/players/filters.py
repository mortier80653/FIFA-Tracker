import django_filters
from .models import DataUsersPlayers


class DataUsersPlayersFilter(django_filters.FilterSet):

    class Meta:
        model = DataUsersPlayers
        fields = {
            'potential': ['gte', 'lte'],
            'overallrating': ['gte', 'lte'],
        }