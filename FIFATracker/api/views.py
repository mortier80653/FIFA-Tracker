from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from players.models import DataNations


# TODO DELETE
class TestViewSet(APIView):
    def get(self, request, format=None):
        usernames = [nat.nationname for nat in DataNations.objects.all()]
        return Response(usernames)

@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'test': reverse('test', request=request, format=format)
    })


