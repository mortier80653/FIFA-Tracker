from django.db.models import Q
from django.contrib.auth.models import User

from players.models import (
    DataUsersTeams,
    DataUsersCareerUsers,
)


def del_session_key(request, key):
    request.session.pop(key, None)


def set_currency(request):
    # Set Currency
    currency_symbols = ('$', '€', '£')
    if request.session.get('currency', None) is None:
        try:
            request.session['currency'] = request.user.profile.currency
        except:
            request.session['currency'] = 1

    if request.session.get('currency_symbol', None) is None:
        request.session['currency_symbol'] = currency_symbols[int(
            request.session['currency'])]


def get_current_user(request):
    # Set current User
    if 'owner' in request.GET:
        owner = request.GET['owner']
        try:
            user = User.objects.get(username=owner)
            is_profile_public = user.profile.is_public
        except Exception as e:
            raise UnknownError(e)

        if not is_profile_public:
            raise PrivateProfileError(
                _("Sorry, {}'s profile is private. Profile visibility can be changed in Control Panel.").format(owner))

        current_user = owner
    elif request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = "guest"

    return current_user


def get_fifa_edition(request):
    try:
        return int(request.user.profile.fifa_edition)
    except Exception:
        return 18


def get_career_user(request, current_user=None):
    if current_user is None:
        current_user = "guest"

    if request.session.get('career_user', None) is None:
        career_user = DataUsersCareerUsers.objects.for_user(current_user).first()

        clubteamid = career_user.clubteamid
        nationalteamid = career_user.nationalteamid
        fteamids = [clubteamid, nationalteamid]
        teams = list(DataUsersTeams.objects.for_user(current_user).filter(Q(teamid__in=fteamids)).iterator())

        clubteamname = ""
        nationalteamname = ""
        for team in teams:
            teamid = team.teamid
            if teamid == clubteamid:
                clubteamname = team.teamname
            elif teamid == nationalteamid:
                nationalteamname = team.teamname

        career_user.clubteamid
        career_user.nationalteamid

        request.session['career_user'] = {
            'clubteamid': clubteamid,
            'clubteamname': clubteamname,
            'nationalteamid': nationalteamid,
            'nationalteamname': nationalteamname,
            'nationalityid': career_user.nationalityid,
        }

    return request.session.get('career_user', None)
