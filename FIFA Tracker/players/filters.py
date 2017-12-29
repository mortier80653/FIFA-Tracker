from django.db.models import Q

class DataUsersPlayersFilter:
    def __init__(self, request_dict, queryset):
        self.request_dict = request_dict
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
        
        return queryset
    
    def order(self, queryset):
        return queryset.order_by('-potential')