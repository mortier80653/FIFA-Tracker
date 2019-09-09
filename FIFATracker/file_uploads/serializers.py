from rest_framework import serializers
from file_uploads.models import CareerSaveFileModel


class CareerSaveFileGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = CareerSaveFileModel
        exclude = ('celery_task_id', 'uploadedfile',)


class CareerSaveFileCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CareerSaveFileModel
        fields = '__all__'
