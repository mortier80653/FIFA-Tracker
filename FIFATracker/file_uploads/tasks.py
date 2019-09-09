import os
import logging
from django.db.models import F

from django.contrib.auth.models import User
from Fifa_Tracker.celery import app
from file_uploads.models import CareerSaveFileModel
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from scripts.process_file_utils import (parse_career_save)


@app.task(queue='process_file_queue')
def process_career_file_task(m_id, slot='1'):
    try:
        save_file_model = CareerSaveFileModel.objects.get(pk=m_id)
    except Exception as e:
        logging.exception("SaveFileDeleted before task?")
        return

    user = save_file_model.user

    def update_savefile_model(cs_model, error, fpath=None):
        if cs_model:
            cs_model.file_process_status_code = 1  # Error Code
            cs_model.file_process_status_msg = error
            cs_model.save()

        try:
            if os.path.exists(fpath):
                os.remove(fpath)
        except PermissionError as e:
            logging.warning("update_savefile_model PermissionError: {}".format(e))
        except TypeError:
            pass

    fpath = os.path.join(settings.MEDIA_ROOT, str(save_file_model.uploadedfile))

    if not os.path.exists(fpath):
        update_savefile_model(save_file_model, _("Save file not found on the server."))
        return False

    careersave_data_path = os.path.join(settings.MEDIA_ROOT, user.username, "data")
    # Parse Career Save
    try:
        fifa_edition = save_file_model.fifa_edition
        parse_career_save(
            career_file_fullpath=fpath,
            data_path=careersave_data_path,
            user=user,
            slot=slot,
            xml_file='',
            fifa_edition=fifa_edition,
            cs_model=save_file_model
        )
        user.profile.is_save_processed = True
        user.profile.fifa_edition = fifa_edition
        user.save()
    except FileNotFoundError as e:
        user.profile.is_save_processed = False
        user.save()
        logging.exception(
            "process_career_file script - ParseCareerSave - user: {}".format(user))
    except Exception as e:
        user.profile.is_save_processed = False
        user.save()
        logging.exception(
            "process_career_file script - ParseCareerSave - user: {}".format(user))
        # delete_data(user_id)
        update_savefile_model(save_file_model, e, fpath=fpath)

    # Update position_in_queue for all objects
    CareerSaveFileModel.objects.all().update(position_in_queue=F('position_in_queue')-1)
