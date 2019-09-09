from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User


def user_dir_path(instance, filename):
    return '{0}/{1}'.format(instance.user.username, 'CareerData')


class CareerSaveFileModel(models.Model):
    def validate_size(filefield_obj):
        filesize = filefield_obj.size
        min_size = 6500000
        max_size = 15000000
        if filesize < min_size:
            raise ValidationError("Your file is not a valid FIFA Career File.")
        elif filesize > max_size:
            raise ValidationError("Your file is not a valid FIFA Career File.")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploadedfile = models.FileField(
        verbose_name='FIFA Career File', upload_to=user_dir_path, validators=[validate_size]
    )
    fifa_edition = models.IntegerField(blank=True, null=True, default=19)
    ft_slot = models.IntegerField(
        blank=True, null=True, default=1
    )
    file_process_status_code = models.IntegerField(
        blank=True, null=True, default=0)
    file_process_status_msg = models.CharField(
        max_length=120, blank=True, null=True)
    position_in_queue = models.IntegerField(blank=True, null=True, default=-1)
    celery_task_id = models.CharField(
        max_length=120, blank=True, null=True
    )
    save_original_name = models.CharField(
        max_length=120, blank=True, null=True
    )
    teamid = models.IntegerField(
        blank=True, null=True, default=0
    )
    ing_date = models.CharField(
        max_length=10, blank=True, null=True, default="20080101"
    )

    # 1 - Manager
    # 2 - Player
    save_type = models.IntegerField(
        blank=True, null=True, default=1
    )

    is_update = models.BooleanField(
        blank=True, default=False
    )
