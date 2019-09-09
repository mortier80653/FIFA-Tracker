from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from django.views.generic import View
from django.http import HttpResponse

import logging
import os
import shutil
import shlex
import subprocess

from collections import Counter

from core.session_utils import del_session_key, set_currency, get_current_user, get_fifa_edition, get_career_user
# from core.tasks import process_career_file_task
from .fifa_utils import get_team_name
from file_uploads.models import CareerSaveFileModel
from .forms import CareerSaveFileForm
from core.consts import (
    SUPPORTED_TABLES,
)
from django.contrib.contenttypes.models import ContentType

from scripts.process_file_utils import delete_from_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from file_uploads.serializers import CareerSaveFileGetSerializer

from .serializers import DataUsersCareerManagerhistorySerializer
from .models import DataUsersCareerManagerhistory
from players.serializers import (
    DataUsersTeamsSerializer,
    DataUsersManagerSerializer,
    DataUsersCareerUsersSerializer,
    DataUsersCareerCalendarSerializer
)
from players.models import (
    DataUsersTeams,
    DataUsersManager,
    DataUsersCareerUsers,
    DataUsersCareerCalendar
)


def upload_career_save_file(request):
    if not request.user.is_authenticated:
        messages.error(request, _(
            'Only authenticated users are allowed to upload files.'))
        return redirect('home')

    # Check if user already uploaded a file and it's not processed yet
    cs_model = CareerSaveFileModel.objects.filter(
        user_id=request.user.id).first()
    user = User.objects.get(username=request.user)

    if cs_model:
        if cs_model.file_process_status_code == 0:
            # File is being processed
            pass
        elif cs_model.file_process_status_code == 1:
            # Error
            cs_model.delete()
        elif cs_model.file_process_status_code == 2:
            # Done
            user.profile.is_save_processed = True
            user.save()
            cs_model.delete()

        return render(request, 'upload.html', {'cs_model': cs_model, 'upload_completed': True})

    if request.method == 'POST':
        form = CareerSaveFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Clear previous save data from session
            del_session_key(request, "career_user")

            fifa_edition = int(request.POST.get('fifa_edition'))

            # Supported FIFA Editions.
            valid_fifa_editions = (17, 18, 19)
            if fifa_edition not in valid_fifa_editions:
                data = {'is_valid': False}
                return JsonResponse(data)

            form = form.save(commit=False)
            form.user = request.user
            form.save()

            user.profile.is_save_processed = False
            user.profile.fifa_edition = fifa_edition
            user.save()

            new_task = process_career_file_task.delay(user.pk, fifa_edition)
            form.celery_task_id = new_task.id
            form.save()

            # # Run "process_career_file.py"
            # if settings.DEBUG:
            #     python_ver = "python"   # My LocalHost
            # else:
            #     python_ver = "python3.6"
            #
            # # python manage.py runscript process_career_file --script-args 14 18
            # command = "{} manage.py runscript process_career_file --script-args {} {}".format(
            #     python_ver, request.user.id, fifa_edition)
            # args = shlex.split(command)
            # subprocess.Popen(args, close_fds=True)

            data = {'is_valid': True}
        else:
            data = {'is_valid': False}

        return JsonResponse(data)
    else:
        form = CareerSaveFileForm()

    return render(request, 'upload.html', {'form': form, 'cs_model': None})


def process_status(request):
    if not request.user.is_authenticated:
        data = {"status": "user not authenticated"}
        return JsonResponse(data)

    cs_model = CareerSaveFileModel.objects.filter(
        user_id=request.user.id).first()
    if cs_model:
        status_code = cs_model.file_process_status_code
        status_msg = cs_model.file_process_status_msg

        if not status_msg:
            status_msg = _("Processing Career Save File.")

        if cs_model.file_process_status_code == 0:
            # File is being processed
            pass
        elif cs_model.file_process_status_code == 1:
            # Error
            cs_model.delete()
        elif cs_model.file_process_status_code == 2:
            # Done
            user = User.objects.get(username=request.user)
            user.profile.is_save_processed = True
            user.save()
            cs_model.delete()

        data = {
            "status_code": status_code,
            "status_msg": status_msg,
        }
    else:
        data = {
            "status_code": 0,
            "status_msg": _("Done?? Try to refresh website."),
        }

    return JsonResponse(data)


def abort_upload(request):
    user = request.user
    if not user.is_authenticated:
        messages.error(request, _('Not authenticated.'))
        return redirect('home')

    logging.info("{} pressed abort button".format(user))

    cs_model = CareerSaveFileModel.objects.filter(user_id=user.id)
    if cs_model:
        # Delete original uploaded file
        for model in cs_model:
            fpath = os.path.join(settings.MEDIA_ROOT, str(model.uploadedfile))
            if os.path.isfile(fpath):
                try:
                    os.remove(fpath)
                    # Delete Model
                    model.delete()
                except PermissionError:
                    messages.error(request, _('File is still processed.'))

    # Delete Files
    careersave_data_path = os.path.join(settings.MEDIA_ROOT, user.username, "data")
    if os.path.exists(careersave_data_path):
        try:
            shutil.rmtree(careersave_data_path)
        except PermissionError:
            messages.error(request, _('File is still processed.'))

    return redirect('home')


def privacypolicy(request):
    return render(request, 'privacy.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def donate(request):
    return render(request, 'donate.html')


def home(request):
    data = User.objects.prefetch_related('careerusers').values(
        'careerusers__clubteamid', 'careerusers__nationalteamid'
    )

    fifa_edition = get_fifa_edition(request)

    clubs = list()
    nationalteams = list()
    all_teams = list()

    for u in data:
        club = u['careerusers__clubteamid']
        if club is not None and int(club) > 0:
            clubs.append(club)
            all_teams.append(club)

        nationalteam = u['careerusers__nationalteamid']
        if (nationalteam is not None) and int(nationalteam) > 0:
            nationalteams.append(nationalteam)
            all_teams.append(nationalteam)

    db_teams = list(DataUsersTeams.objects.for_user(
        "guest").all().filter(Q(teamid__in=all_teams)).values())

    count_all_teams = Counter(all_teams).most_common()

    max_teams_display = 30  # Max number of most popular teams to be displayed on homepage
    users_clubs = list()
    users_nationalteams = list()
    teamname = ""
    for team in count_all_teams:
        teamname = get_team_name(db_teams, team[0])
        if team[0] in clubs and len(users_clubs) < max_teams_display:
            users_clubs.append(
                {'id': team[0], 'managers': team[1], 'teamname': teamname, })
        elif team[0] in nationalteams and len(users_nationalteams) < max_teams_display:
            users_nationalteams.append(
                {'id': team[0], 'managers': team[1], 'teamname': teamname, })

    context = {
        'users_clubs': users_clubs,
        'users_nationalteams': users_nationalteams,
        'fifa_edition': fifa_edition,
    }
    return render(request, 'home.html', context=context)


class CareerSaveDelete(APIView):
    # authentication_classes = [JSONWebTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.data['to_delete'] == "cs_model":
            try:
                save_file_model = CareerSaveFileModel.objects.get(pk=request.data['model_id'])
                save_file_model.delete()
            except Exception as e:
                logging.exception("SaveFileDeleted before task?")
                return

            return Response({})

        elif request.data['to_delete'] == "slot":
            user_id = request.user.id
            slot_id = request.data['slot_id']

            try:
                fifa_edition = request.user.profile.slots_data[slot_id]['fifa_edition']
            except KeyError:
                fifa_edition = "19"

            for table in SUPPORTED_TABLES:
                if table == "players":
                    if fifa_edition == '18':
                        table = "players"
                    else:
                        table = "players{}".format(fifa_edition)

                model_name = "datausers{}".format(table.replace("_", ""))

                ct = ContentType.objects.get(model=model_name)
                model = ct.model_class()

                # if ft_season == -1 then delete whole slot
                delete_from_model(model=model, user_id=user_id, ft_slot=slot_id, ft_season=-1)

            slots_data = request.user.profile.slots_data
            slots_data.pop(slot_id, None)
            request.user.profile.slots_data = slots_data
            request.user.save()

            return Response({})


class CareerSavesGet(APIView):
    # authentication_classes = [JSONWebTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # In Progress
        kwargs = {
            'user_id': request.user.id,
        }

        serializer_in_progress = CareerSaveFileGetSerializer(
            CareerSaveFileModel.objects.filter(**kwargs),
            many=True
        ).data

        # Completed
        kwargs = {
            'ft_user_id': request.user.id,
        }
        serializer_completed = DataUsersCareerUsersSerializer(
            DataUsersCareerUsers.objects.filter(**kwargs),
            many=True
        ).data

        serializer_manager = DataUsersManagerSerializer(
            DataUsersManager.objects.filter(**kwargs),
            many=True
        ).data

        serializer_teams = DataUsersTeamsSerializer(
            DataUsersTeams.objects.filter(**kwargs),
            many=True
        ).data

        serializer_calendar = DataUsersCareerCalendarSerializer(
            DataUsersCareerCalendar.objects.filter(**kwargs),
            many=True
        ).data

        serializer_manager_hist = DataUsersCareerManagerhistorySerializer(
            DataUsersCareerManagerhistory.objects.filter(**kwargs),
            many=True
        ).data

        def get_data(
            save_slot,
            completed,
            in_progress,
            manager_hist,
            calendar,
            managers,
            teams
        ):
            for save in in_progress:
                if save_slot == save['ft_slot']:
                    return save

            max_season = 0
            result = {}
            # Data from latest season
            for save in completed:
                if save_slot != save['ft_slot']:
                    continue
                if save['ft_season'] <= max_season:
                    continue
                result = save
            if not result:
                return {}

            for m in managers:
                if save_slot != m['ft_slot']:
                    continue
                if result['ft_season'] != m['ft_season']:
                    continue
                if result['clubteamid'] != m['teamid']:
                    continue

                result['headid'] = m['headid']
                break

            for t in teams:
                if save_slot != t['ft_slot']:
                    continue
                if result['ft_season'] != t['ft_season']:
                    continue
                if result['clubteamid'] != t['teamid']:
                    continue
                result.update({
                    "team_power": {
                        'ovr': t['overallrating'],
                        'att': t['attackrating'],
                        'mid': t['midfieldrating'],
                        'def': t['defenserating'],
                    }
                })
                break

            keys = [
                'games_played', 'goals_against',
                'goals_for', 'wins', 'draws', 'losses'
            ]

            hist = {}
            for k in keys:
                hist[k] = 0

            for f in manager_hist:
                if result['ft_slot'] != f['ft_slot']:
                    continue

                for k in keys:
                    hist[k] += f[k]

            result.update({
                "m_hist": hist
            })

            for f in calendar:
                if result['ft_slot'] != f['ft_slot']:
                    continue
                if result['ft_season'] != f['ft_season']:
                    continue

                season_display = "{}/{}".format(
                    str(f['setupdate'])[2:4],
                    str(f['enddate'])[2:4],
                )

                result.update({
                    "season_display": season_display
                })
                break

            return result

        filtered = []

        MAX_SLOTS = 10
        for slot in range(1, MAX_SLOTS+1):
            data = get_data(
                slot, serializer_completed, serializer_in_progress,
                serializer_manager_hist, serializer_calendar, serializer_manager,
                serializer_teams
            )

            filtered.append(
                data
            )

        return Response({
            'saves': filtered,
            'in_progress': serializer_in_progress,
            # 'completed': serializer_completed,
        })


class FrontendAppView(View):
    """
    Serves the compiled frontend entry point (only works if you have run `yarn
    run build`).
    """

    def get(self, request):
        try:
            with open(os.path.join(settings.BASE_DIR, 'frontend', 'build', 'index.html')) as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            logging.exception('Production build of app not found')
            return HttpResponse(
                """
                This URL is only used when you have built the production
                version of the app. Visit http://localhost:3000/ instead, or
                run `yarn run build` to test the production version.
                """,
                status=501,
            )
