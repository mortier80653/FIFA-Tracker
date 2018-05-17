import logging

from django.shortcuts import render
from django.http import JsonResponse

from core.fifa_utils import PlayerWage, PlayerValue
from players.models import (
    DataUsersTeams, 
    DataUsersLeagues,
    DataUsersLeagueteamlinks, 
)


def ajax_calcpot(request):
    try:
        currency = int(request.GET.get('currency') or 1)
        player_value = int(request.GET.get('player_value') or 0)
        positionid = int(request.GET.get('positionid') or 25)
        age = int(request.GET.get('age') or 0)
        ovr = int(request.GET.get('ovr') or 0)

        possible_potential = list()
        for pot in range(ovr, 100):
            calc_player_value = PlayerValue(ovr=ovr, pot=pot, age=age, posid=positionid, currency=currency).value
            if calc_player_value == player_value:
                possible_potential.append(pot)

            if calc_player_value > player_value:
                break
        
        if possible_potential:
            if len(possible_potential) == 1:
                result = "The potential of this player is {} or less.".format(possible_potential[0])
            else:
                result = "The potential of this player is {}-{}".format(possible_potential[0], possible_potential[-1])
        else:
            result = "Player potential calculation has failed. Invalid player value?"
    except Exception as e:
        e = str(e)
        logging.error("ajax_calcpot error: {}".format(e))
        result = "Error: {}".format(e)          

    return JsonResponse({'result': result})

def ajax_calcwage(request):
    try:
        if request.user.is_authenticated:
            current_user = request.user
        else:
            current_user = "guest"

        currency = int(request.GET.get('currency') or 1)

        teamid = (request.GET.get('teamid') or "5") # 5 == Chelsea
        if "," in teamid:
            teamid = int(teamid.split(",")[0])
        else:
            teamid = int(teamid)

        leagueid = (request.GET.get('leagueid') or 0)
        
        if leagueid == 0:
            leagueid = DataUsersLeagueteamlinks.objects.for_user(current_user).filter(teamid=teamid).first().leagueid
        else:
            if "," in leagueid:
                leagueid = int(leagueid.split(",")[0])
            else:
                leagueid = int(leagueid)

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
        result = "Weekly wage of a {} yo, {} rated player playing for {} in {} league is {} {}".format(age, ovr, team.teamname, league.leaguename, wage, currency_symbols[currency])
    except Exception as e:
        e = str(e)
        logging.error("ajax_calcwage error: {}".format(e))
        result = "Error: {}".format(e) 

    return JsonResponse({'result': result})

def calculator(request):
    return render(request, 'tools/calculator.html')
