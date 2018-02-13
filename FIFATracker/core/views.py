from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User

from collections import Counter

from .fifa_utils import get_team_name
from players.models import DataUsersTeams
from .models import CareerSaveFileModel
from .forms import CareerSaveFileForm

def upload_career_save_file(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Only authenticated users are allowed to upload files.')
        return redirect('home')

    # Check if user already uploaded a file and it's not processed yet
    if CareerSaveFileModel.objects.filter(user_id=request.user.id):
        messages.error(request, "You cannot upload new file if the previous one hasn't been processed.")
        return render(request, 'upload.html', {'upload_completed': True} )   

    if request.method == 'POST':
        form = CareerSaveFileForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            messages.success(request, "Upload completed.")
            return render(request, 'upload.html', {'upload_completed': True} )   
    else:
        form = CareerSaveFileForm()

    return render(request, 'upload.html', {'form':form})    

def privacypolicy(request):
    return render(request, 'privacy.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def donate(request):
    return render(request, 'donate.html')

def home(request):
    data = User.objects.prefetch_related('careerusers').values('careerusers__clubteamid', 'careerusers__nationalteamid')
    
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

    db_teams = list(DataUsersTeams.objects.for_user("guest").all().filter(Q(teamid__in=all_teams)).values())

    
    count_all_teams = Counter(all_teams).most_common()

    max_teams_display = 30 # Max number of most popular teams to be displayed on homepage
    users_clubs = list()
    users_nationalteams = list()
    teamname = ""
    for team in count_all_teams:
        teamname = get_team_name(db_teams, team[0])
        if team[0] in clubs and len(users_clubs) < max_teams_display:
            users_clubs.append({'id': team[0], 'managers': team[1], 'teamname': teamname, })
        elif team[0] in nationalteams and len(users_nationalteams) < max_teams_display:
            users_nationalteams.append({'id': team[0], 'managers': team[1], 'teamname': teamname, })

    context = {'users_clubs':users_clubs, 'users_nationalteams':users_nationalteams, }
    return render(request, 'home.html', context=context)