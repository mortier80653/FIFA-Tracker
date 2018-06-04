
from datetime import date, datetime, timedelta
from django.conf import settings  
from json import dumps
from accounts.models import Profile

class LastUserActivityMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                last_activity = datetime.strptime(request.session.get("last-activity"), '"%Y-%m-%d %H:%M:%S.%f"')
            except (ValueError, TypeError):
                last_activity = None
            
            # If key is old enough, update database.
            too_old_time = datetime.now() - timedelta(seconds=settings.LAST_ACTIVITY_INTERVAL_SECS)
            if not last_activity or last_activity < too_old_time:
                Profile.objects.filter(user_id=request.user.id).update(
                        last_activity=dumps(datetime.now(), default=self.json_serial),)

            request.session["last-activity"] = dumps(datetime.now(), default=self.json_serial)

        return None

    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, (datetime, date)):
            return obj.strftime("%Y-%m-%d %H:%M:%S.%f")
        raise TypeError ("Type %s not serializable" % type(obj))