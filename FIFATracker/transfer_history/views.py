from django.shortcuts import render, redirect
from django.contrib import messages
from core.exceptions import NoResultsError, PrivateProfileError, UnknownError
from core.generate_view_helper import get_transfers

def transfers(request):
    try:
        additional_filters = dict()
        if not 'result' in request.GET:
            additional_filters = {'result': 32}

        context = get_transfers(request, additional_filters=additional_filters, paginate=True)
        return render(request, 'transfer_history/transfers.html', context)
    except (NoResultsError, PrivateProfileError, UnknownError) as e:
        messages.error(request, e)
        return redirect('home')
