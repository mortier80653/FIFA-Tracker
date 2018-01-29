from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    USDOLLAR = 0
    EURO = 1
    POUND = 2
    CURRENCY_CHOICES = (
        (USDOLLAR, 'USD'),
        (EURO, 'Euro'),
        (POUND, 'Pound'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,)
    currency = models.CharField(max_length=1, choices=CURRENCY_CHOICES, default=EURO)
    unit_system = models.BooleanField(default=0) # 0 - Metric, 1 - Imperial
    is_public = models.BooleanField(default=0)
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()