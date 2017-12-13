import time

from django.shortcuts import render, redirect
from .models import *
from django.db import connection

from .fifa_utils import FifaPlayer, PlayerAge, PlayerValue, PlayerWage, FifaDate

def players(request):
    start = time.time()
    positions = ('GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM', 'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW')

    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "test123"

    data = DataUsersPlayers.objects.for_user(current_user).filter(preferredposition1=27).order_by('-overallrating')[:40]

    # Current date according to in-game calendar
    current_date = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate   
    
    for obj in data:
        fifa_player = FifaPlayer(obj,current_user, current_date)
        setattr(obj, 'test', fifa_player)
        team_player_links = DataUsersTeamplayerlinks.objects.for_user(current_user).filter(playerid=obj.playerid)
        # Team-Player links 
        for team in team_player_links:
            player_team = DataUsersTeams.objects.for_user(current_user).filter(teamid=team.teamid)[0]
            teamid = team.teamid
            teamname = player_team.teamname
            if player_team.cityid > 0:   
                break
        
        # Player Name
        try:
            if obj.commonname_id > 0:
                setattr(obj, 'playername', obj.commonname.name)
            else:
                setattr(obj, 'playername', " ".join((obj.firstname.name, obj.lastname.name)))
        except DataPlayernames.DoesNotExist:
            try:
                getnames = DataUsersEditedplayernames.objects.for_user(current_user).get(playerid=obj.playerid)
                if getnames.commonname:
                    setattr(obj, 'playername', getnames.commonname)
                else:
                    setattr(obj, 'playername', " ".join((getnames.firstname , getnames.surname)))
            except DataUsersEditedplayernames.DoesNotExist:
                setattr(obj, 'playername', obj.commonname_id)

        # Player Age
        pAge = PlayerAge(obj.birthdate, current_date).age
        setattr(obj, 'age', pAge)

        # Calculate player value
        pValue = PlayerValue(obj.overallrating, obj.potential, obj.age, obj.preferredposition1, currency=1).playervalue
        setattr(obj, 'value', "{:,}".format(pValue))

        # Calculate player wage
        leagueid = DataUsersLeagueteamlinks.objects.for_user(current_user).filter(teamid=teamid)[0].leagueid
        pWage = PlayerWage(obj.overallrating, pAge, obj.preferredposition1, leagueid, player_team.domesticprestige, player_team.profitability).playerwage
        setattr(obj, 'wage', "{:,}".format(pWage))

        # Preffered player positions
        obj.preferredposition1 = positions[obj.preferredposition1]
        if obj.preferredposition2 >= 0: obj.preferredposition2 = positions[obj.preferredposition2]
        if obj.preferredposition3 >= 0: obj.preferredposition3 = positions[obj.preferredposition3]
        if obj.preferredposition4 >= 0: obj.preferredposition4 = positions[obj.preferredposition4]

        # Player Contract #


        # Player Join Team Date
        pJoinTeamDate = FifaDate(obj.playerjointeamdate).date
        setattr(obj, 'joined_year', pJoinTeamDate.year)

        # Check if player is loaned out
        try:
            onloan = DataUsersPlayerloans.objects.for_user(current_user).get(playerid=obj.playerid)
            loanedto_teamid = teamid
            loanedto_teamname = teamname
            teamid = onloan.teamidloanedfrom
            teamname = DataUsersTeams.objects.for_user(current_user).get(teamid=teamid).teamname
            setattr(obj, 'loanedto_clubid', loanedto_teamid)
            setattr(obj, 'loanedto_clubname', loanedto_teamname)
            setattr(obj, 'isloanedout', 1)
        except DataUsersPlayerloans.DoesNotExist: 
            setattr(obj, 'isloanedout', 0)

        setattr(obj, 'club', teamname)
        setattr(obj, 'clubid', teamid)
    
    endtime = time.time() - start
    print ("Loading time: {} Queries: {}".format(endtime, len(connection.queries)))
    return render(request, 'players/players.html', {'data':data})

def player(request, playerid):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "test123"

    try:
        data = DataUsersPlayers.objects.for_user(current_user).get(playerid=playerid)
    except DataUsersPlayers.DoesNotExist: 
        return redirect('players')

    return render(request, 'players/player.html', {'data':data})