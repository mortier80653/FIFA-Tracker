from rest_framework import serializers
from .models import (
    DataUsersTeams,
    DataUsersManager,
    DataUsersCareerUsers,
    DataUsersCareerCalendar,
)


class DataUsersTeamsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataUsersTeams
        exclude = ('primary_key',)


class DataUsersManagerSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataUsersManager
        exclude = ('primary_key',)


class DataUsersCareerUsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataUsersCareerUsers
        exclude = ('primary_key',)


class DataUsersCareerCalendarSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataUsersCareerCalendar
        exclude = ('primary_key',)
