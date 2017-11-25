from django.shortcuts import render
from .models import Players, Teamplayerlinks, Playernames, Editedplayernames

from .fifa_utils import PlayerAge, PlayerValue

def calcAge(birtydaydate):
    currdate = date(2017, 1, 1)
    startdate = date(1582, 10, 14)
    birthdate = startdate + timedelta(days=birtydaydate)
    return currdate.year - birthdate.year - ((currdate.month, currdate.day) < (birthdate.month, birthdate.day))


def players(request):
    positions = ('GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM', 'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW')
    #data = Players.objects.order_by('-potential')[:40]
    data = Players.objects.order_by('-overallrating')[:40]
    for obj in data:
        setattr(obj, 'isnameedited', 0)

        getlinks = Teamplayerlinks.objects.filter(playerid=obj.playerid)

        #if cityid == 0 then it's National Team
        if getlinks.count() == 2 and getlinks[0].teamid.cityid == 0:
            getlinks = getlinks[1]
        else:
            getlinks = getlinks[0]

        try:
            obj.firstname
        except Playernames.DoesNotExist:
            getnames = Editedplayernames.objects.get(playerid=obj.playerid)
            setattr(obj, 'isnameedited', 1)
            setattr(obj, 'edited_firstname', getnames.firstname)
            setattr(obj, 'edited_surname', getnames.surname)

        pAge = PlayerAge(obj.birthdate).age
        setattr(obj, 'age', pAge)
        pValue = PlayerValue(obj.overallrating, obj.potential, obj.age, obj.preferredposition1, currency=1).playervalue
        setattr(obj, 'value', "{:,}".format(pValue))

        obj.preferredposition1 = positions[obj.preferredposition1]
        if obj.preferredposition2 > 0: obj.preferredposition2 = positions[obj.preferredposition2]
        if obj.preferredposition3 > 0: obj.preferredposition3 = positions[obj.preferredposition3]
        if obj.preferredposition4 > 0: obj.preferredposition4 = positions[obj.preferredposition4]

        setattr(obj, 'isregen', 0)
        setattr(obj, 'club', getlinks.teamid.teamname)
        setattr(obj, 'clubid', getlinks.teamid.teamid)

    return render(request, 'players.html', {'data':data})