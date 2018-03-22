import os

from django.conf import settings
from django.contrib.auth.models import User
from core.models import CareerSaveFileModel

from scripts.process_file_utils import ParseCareerSave
from scripts.delete_user_data import delete_data

def update_savefile_model(user_id, error, fpath=None):
    cs_model = CareerSaveFileModel.objects.filter(user_id=user_id).first()
    if cs_model:
        cs_model.file_process_status_code = 1   # Error Code
        cs_model.file_process_status_msg = error
        cs_model.save()

    try:
        if os.path.exists(fpath):
            os.remove(fpath)
    except PermissionError as e:
        print("PermissionError: {}".format(e))
    except TypeError:
        pass



def run(*args):
    user_id = args[0]
    fifa_edition = args[1]  

    user = User.objects.get(id=user_id)
    if not user:
        print("User not found, ID:{}".format(user_id))
        return

    save_file_model = CareerSaveFileModel.objects.filter(user_id=user.id).first()
    if not save_file_model:
        update_savefile_model(user_id, "Save file model not found.")
        return

    # Path to meta XML file for a FIFA database.
    FIFA_XML_PATH = os.path.join(settings.BASE_DIR, "scripts", "Data", fifa_edition, "XML", "fifa_ng_db-meta.xml") 
    
    fpath = os.path.join(settings.MEDIA_ROOT, str(save_file_model.uploadedfile))
    if not os.path.exists(fpath):
        update_savefile_model(user_id, "Save file not found on the server.")
        return

    careersave_data_path = os.path.join(settings.MEDIA_ROOT, user.username, "data")
    
    # Parse Career Save
    try:
        ParseCareerSave(career_file_fullpath=fpath, careersave_data_path=careersave_data_path, user=user, xml_file=FIFA_XML_PATH, fifa_edition=fifa_edition)
        user.profile.is_save_processed = True
        user.profile.fifa_edition = fifa_edition
        user.save()
    except Exception as e:
        user.profile.is_save_processed = False
        user.save()
        print(e)
        delete_data(user_id)
        update_savefile_model(user_id, e, fpath=fpath)


        
        
    