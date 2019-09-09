from django.conf import settings
import time
import os
import pyrabbit
import logging

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    CareerSaveFileGetSerializer,
    CareerSaveFileCreateSerializer,
)
from .models import CareerSaveFileModel
from file_uploads.tasks import process_career_file_task
from scripts.process_file_utils import get_basic_cm_save_info


# RabbitMQ API
RABBIT_API = pyrabbit.api.Client(
    settings.RABITMQ_API_URL,
    settings.RABITMQ_API_USER,
    settings.RABITMQ_API_PASS,
)


class CareerSaveFileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    # authentication_classes = [JSONWebTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.data.update({
            'user': request.user.id,
            'file_process_status_code': -1
        })

        serializer = CareerSaveFileCreateSerializer(data=request.data)

        if serializer.is_valid():
            saved = serializer.save()

            fpath = os.path.join(settings.MEDIA_ROOT, str(saved.uploadedfile))

            if os.path.exists(fpath):
                basic_info = get_basic_cm_save_info(fpath)
                saved.save_original_name = basic_info['save_original_name']
                saved.teamid = basic_info['teamid']
                saved.ing_date = basic_info['ing_date']
                saved.save_type = basic_info['save_type']
                saved.save()

            created_task = process_career_file_task.delay(
                saved.id, slot=str(saved.ft_slot)
            )

            attempts = 0
            while attempts <= 5:
                try:
                    pos_in_queue = RABBIT_API.get_queue('/', 'process_file_queue')['messages']
                    break
                except pyrabbit.http.NetworkError:
                    attempts += 1
                    logging.exception("Broken Pipe?")
                    pos_in_queue = -1
                    time.sleep(0.3)

            saved.celery_task_id = created_task.id
            saved.position_in_queue = pos_in_queue
            saved.save()

            return Response({
                'position_in_queue': pos_in_queue,
                'save_original_name': saved.save_original_name,
                'teamid': saved.teamid,
                'ing_date': saved.ing_date,
                'id': saved.id,
            }, status=status.HTTP_201_CREATED)
        else:
            print('error', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
