from django.db import models
from django.contrib.auth.models import User

def user_dir_path(instance, filename):
    return '{0}/{1}'.format(instance.user.username, 'CareerData')

class CareerSaveFileModel(models.Model):
    user = models.ForeignKey(User)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploadedfile = models.FileField(upload_to=user_dir_path)