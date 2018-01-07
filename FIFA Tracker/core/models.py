from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

def user_dir_path(instance, filename):
    return '{0}/{1}'.format(instance.user.username, 'CareerData')

class CareerSaveFileModel(models.Model):
    def validate_size(filefield_obj):
        filesize = filefield_obj.file.size
        max_size = 15000000
        if filesize > max_size:
            raise ValidationError("Your file is not a FIFA 18 Career File.")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploadedfile = models.FileField(verbose_name='FIFA 18 Career File', upload_to=user_dir_path, validators=[validate_size])

