from django.shortcuts import render
from django.http import JsonResponse

from core.fifa_utils import PlayerWage, PlayerValue
from players.models import (
    DataUsersTeams, 
    DataUsersLeagues, 
)


def ajax_calcpot(request):
    currency = int(request.GET.get('currency') or 1)
    player_value = int(request.GET.get('player_value') or 0)
    positionid = int(request.GET.get('positionid') or 25)
    age = int(request.GET.get('age') or 0)
    ovr = int(request.GET.get('ovr') or 0)

    values = dict()
    for pot in range(ovr, 100):
        values[pot] = PlayerValue(ovr=ovr, pot=pot, age=age, posid=positionid, currency=currency).value
        if values[pot] == player_value:
            break

    for key in values:
        if values[key] == player_value:
            result = "The potential of this player is {} or less.".format(key)
            break
        elif values[key] > player_value:
            result = "The potential of this player is {} or less.".format(key)
            break
        else:
            result = "Player potential calculation has failed."

    return JsonResponse({'result': result})

def ajax_calcwage(request):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "guest"

    currency = int(request.GET.get('currency') or 1)
    leagueid = (request.GET.get('leagueid') or "13") # 13 == ENG (1)
    if "," in leagueid:
        leagueid = int(leagueid.split(",")[0])
    else:
        leagueid = int(leagueid)
    
    teamid = (request.GET.get('teamid') or "5") # 5 == Chelsea
    if "," in teamid:
        teamid = int(teamid.split(",")[0])
    else:
        teamid = int(teamid)

    positionid = int(request.GET.get('positionid') or 25)
    age = int(request.GET.get('age') or 0)
    ovr = int(request.GET.get('ovr') or 0)

    team = DataUsersTeams.objects.for_user(current_user).filter(teamid=teamid).first()

    league = DataUsersLeagues.objects.for_user(current_user).filter(leagueid=leagueid).first()

    player_team = {
        "league": {"leagueid": league.leagueid},
        "team": {"domesticprestige": team.domesticprestige, "profitability": team.profitability},
    }

    wage = PlayerWage(ovr=ovr, age=age, posid=positionid, player_team=player_team, currency=currency).formated_wage

    currency_symbols = ('$', '€', '£')
    result = "Weekly wage of a player playing for {} in {} league is {} {}".format(team.teamname, league.leaguename, wage, currency_symbols[currency])

    return JsonResponse({'result': result})

def calculator(request):
    return render(request, 'tools/calculator.html')
