import datetime
import logging

from django.contrib.auth.models import User

from scripts.delete_user_data import delete_data

def cleardb():
    # Delete inactive users career data.
    logging.info("cleardb script - START")

    now = datetime.datetime.now()

    inactive_users = list()
    users = User.objects.all()

    for user in users:
        try:
            last_activity = datetime.datetime.strptime(user.profile.last_activity, '"%Y-%m-%d %H:%M:%S.%f"')
            since_last_activity = now - last_activity
            
            # Delete data after 28 days of inactivity
            if since_last_activity.days >= 28:
                inactive_users.append(user.id)

        except ValueError:
            # No activity at all.
            inactive_users.append(user.id)
        except TypeError:
            logging.exception("cleardb script - user: {}".format(user))
            continue

    logging.info("cleardb script - Inactive users - {}".format(inactive_users))
    delete_data(inactive_users)
    logging.info("cleardb script - DONE")

# python manage.py runscript cleardb
def run(*args):
    cleardb()
