from django.forms import widgets
from rest_framework import serializers
from players.models import DataNations
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User


class TestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataNations
        fields = ('nationname')

