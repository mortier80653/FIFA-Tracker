from django.shortcuts import render
from .models import DataUsersPlayers, DataUsersTeams, DataUsersTeamplayerlinks, DataPlayernames, DataUsersLeagueteamlinks, DataUsersEditedplayernames, DataUsersCareerCalendar, DataUsersCareerUsers
from django.db import connection

from .fifa_utils import PlayerAge, PlayerValue, PlayerWage, PlayerJoinTeamDate

def players(request):
    positions = ('GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM', 'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW')

    if request.user.is_authenticated():
        current_user = request.user
    else:
        current_user = "test123"

    data = DataUsersPlayers.objects.for_user(current_user).order_by('-potential')[:40]

    # Current date in-game
    currdate = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate   
    
    for obj in data:
        team_player_links = DataUsersTeamplayerlinks.objects.for_user(current_user).filter(playerid=obj.playerid)
        
        # Team-Player links 
        for team in team_player_links:
            player_team = DataUsersTeams.objects.for_user(current_user).filter(teamid=team.teamid)[0]
            teamid = team.teamid
            if player_team.cityid > 0:   
                break
        
        # Player Name
        try:
            if obj.commonname_id > 0:
                setattr(obj, 'playername', obj.commonname.name)
            else:
                setattr(obj, 'playername', " ".join((obj.firstname.name, obj.lastname.name)))
        except DataPlayernames.DoesNotExist:
            getnames = DataUsersEditedplayernames.objects.for_user(current_user).filter(playerid=obj.playerid)[0]
            if getnames.commonname:
                setattr(obj, 'playername', getnames.commonname)
            else:
                setattr(obj, 'playername', " ".join((getnames.firstname , getnames.surname)))

        # Player Join Team Date
        pJoinTeamDate = PlayerJoinTeamDate(obj.playerjointeamdate)
        setattr(obj, 'joined_year', pJoinTeamDate.jointeamyear)

        # Player Age
        pAge = PlayerAge(obj.birthdate, currdate).age
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

        setattr(obj, 'isregen', 0)
        setattr(obj, 'club', player_team.teamname)
        setattr(obj, 'clubid', teamid)
    
    print ("Queries: {}".format(len(connection.queries)))
    return render(request, 'players.html', {'data':data})