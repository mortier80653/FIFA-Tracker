from django.shortcuts import render
from .models import DataUsersPlayers, DataUsersTeams, DataUsersTeamplayerlinks, DataPlayernames, DataUsersLeagueteamlinks, DataUsersEditedplayernames, DataUsersCareerCalendar, DataUsersCareerUsers
from django.db import connection

from .fifa_utils import PlayerAge, PlayerValue, PlayerWage

def players(request):
    positions = ('GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM', 'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW')

    if request.user.is_authenticated():
        current_user = request.user
    else:
        current_user = "test123"

    data = DataUsersPlayers.objects.for_user(current_user).order_by('-overallrating')[:40]
    currdate = DataUsersCareerCalendar.objects.for_user(current_user)[0].currdate
    

    for obj in data:
        setattr(obj, 'isnameedited', 0)

        team_player_links = DataUsersTeamplayerlinks.objects.for_user(current_user).filter(playerid=obj.playerid)
        teamid = team_player_links[0].teamid
        player_team = DataUsersTeams.objects.for_user(current_user).filter(teamid=teamid)
        leagueid = DataUsersLeagueteamlinks.objects.for_user(current_user).filter(teamid=teamid)[0].leagueid
        print(teamid)
        print(leagueid)
        #if cityid == 0 then it's National Team
        if player_team.count() == 2 and player_team[0].cityid == 0:
            player_team = player_team[1]
        else:
            player_team = player_team[0]

        setattr(obj, 'club', player_team.teamname)
        setattr(obj, 'clubid', player_team.teamid)

        try:
            obj.firstname
        except DataPlayernames.DoesNotExist:
            getnames = DataUsersEditedplayernames.objects.filter(playerid=obj.playerid)[0]
            setattr(obj, 'isnameedited', 1)
            setattr(obj, 'edited_firstname', getnames.firstname)
            setattr(obj, 'edited_surname', getnames.surname)

        pAge = PlayerAge(obj.birthdate, currdate).age
        setattr(obj, 'age', pAge)
        pValue = PlayerValue(obj.overallrating, obj.potential, obj.age, obj.preferredposition1, currency=1).playervalue
        setattr(obj, 'value', "{:,}".format(pValue))

        pWage = PlayerWage(obj.overallrating, pAge, obj.preferredposition1, leagueid, player_team.domesticprestige, player_team.profitability).playerwage
        setattr(obj, 'wage', "{:,}".format(pWage))

        obj.preferredposition1 = positions[obj.preferredposition1]
        if obj.preferredposition2 > 0: obj.preferredposition2 = positions[obj.preferredposition2]
        if obj.preferredposition3 > 0: obj.preferredposition3 = positions[obj.preferredposition3]
        if obj.preferredposition4 > 0: obj.preferredposition4 = positions[obj.preferredposition4]

        setattr(obj, 'isregen', 0)
        #setattr(obj, 'club', team_player_links.teamid[0].teamname[0])
        #setattr(obj, 'clubid', team_player_links.teamid[0].teamid[0])
    
    print ("Queries: {}".format(len(connection.queries)))
    return render(request, 'players.html', {'data':data})