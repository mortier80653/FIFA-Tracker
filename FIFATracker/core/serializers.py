from django.forms import widgets
from rest_framework import serializers
from players.models import DataNations
from django.contrib.auth.models import User
from .models import DataUsersCareerManagerhistory


class TestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataNations
        fields = ('nationname')


class DataUsersCareerManagerhistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = DataUsersCareerManagerhistory
        exclude = ('primary_key', 'artificialkey',)
