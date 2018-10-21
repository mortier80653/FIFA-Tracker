from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from core.generate_view_helper import get_fifaplayers
from core.exceptions import NoResultsError, PrivateProfileError, UnknownError, UserNotExists

def player(request, playerid=None):
    context = {}
    if playerid:
        try:
            additional_filters = {'playerid': playerid}
            player = get_fifaplayers(
                request, additional_filters=additional_filters, paginate=False)

            context = {'p': player['players'][0]}
        except NoResultsError:
            messages.error(request, _("Invalid PlayerID ({})".format(playerid)))
            return redirect('home')
        except (PrivateProfileError, UnknownError, UserNotExists) as e:
            messages.error(request, e)
            return redirect('home')

    return render(request, 'editor/edit_player.html', context)
