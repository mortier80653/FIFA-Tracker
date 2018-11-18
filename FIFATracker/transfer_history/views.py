from django.shortcuts import render, redirect
from django.contrib import messages
from core.exceptions import NoResultsError, PrivateProfileError, UnknownError
from core.generate_view_helper import get_transfers
from core.session_utils import get_fifa_edition


def transfers(request):
    try:
        additional_filters = dict()
        fifa_edition = get_fifa_edition(request)
        if 'result' not in request.GET and fifa_edition != 19:
            additional_filters = {'result': 32}

        context = get_transfers(
            request, additional_filters=additional_filters, paginate=True, fifa_edition=fifa_edition,
        )
        return render(request, 'transfer_history/transfers.html', context)
    except (NoResultsError, PrivateProfileError, UnknownError) as e:
        messages.error(request, e)
        return redirect('home')
