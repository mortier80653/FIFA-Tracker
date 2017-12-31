from django.db.models import Q
from .fifa_utils import FifaDate

class DataUsersPlayersFilter:
    def __init__(self, request_dict, queryset, current_date):
        self.request_dict = request_dict
        self.current_date = current_date
        queryset = self.filter(queryset)
        queryset = self.order(queryset)
        self.qs = queryset

    def filter(self, queryset):
        try:
            if 'overallrating__gte' and 'overallrating__lte' in self.request_dict:
                queryset = queryset.filter(Q(overallrating__gte=self.request_dict['overallrating__gte']), Q(overallrating__lte=self.request_dict['overallrating__lte']))
        except ValueError:
            pass

        try:
            if 'potential__gte' and 'potential__lte' in self.request_dict:
                queryset = queryset.filter(Q(potential__gte=self.request_dict['potential__gte']), Q(potential__lte=self.request_dict['potential__lte']))
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
            if 'height__gte' and 'height__lte' in self.request_dict:
                queryset = queryset.filter(Q(height__gte=self.request_dict['height__gte']), Q(height__lte=self.request_dict['height__lte']))
        except ValueError:
            pass

        try:
            if 'weight__gte' and 'weight__lte' in self.request_dict:
                queryset = queryset.filter(Q(weight__gte=self.request_dict['weight__gte']), Q(weight__lte=self.request_dict['weight__lte']))
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