import logging
from datetime import date, datetime, timedelta
from django.conf import settings
from json import dumps
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from accounts.models import Profile


class LastUserActivityMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        try:
            user = JWTAuthentication().authenticate(request)[0]
        except InvalidToken:
            return None
        except Exception:
            logging.exception("LastUserActivityMiddleware")
            return None

        if user:
            try:
                last_activity = datetime.strptime(
                    user.profile.last_activity.replace('"', ''),
                    '%Y-%m-%d %H:%M:%S.%f'
                )
            except (ValueError, TypeError) as e:
                logging.exception("LastUserActivityMiddleware - {}".format(user.profile.last_activity))
                last_activity = datetime(2008, 6, 4, 16, 46, 22, 179423)

            # If key is old enough, update database.
            too_old_time = datetime.now() - timedelta(seconds=settings.LAST_ACTIVITY_INTERVAL_SECS)
            if not last_activity or last_activity < too_old_time:
                user.profile.last_activity = dumps(datetime.now(), default=self.json_serial)
                user.save()

        return None

    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, (datetime, date)):
            return obj.strftime("%Y-%m-%d %H:%M:%S.%f")
        raise TypeError("Type %s not serializable" % type(obj))
