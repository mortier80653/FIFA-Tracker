from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from django.contrib.auth.models import User

def ajax_change_currency(request):
    currency = request.GET.get('currency', 1)

    if int(currency) not in range(0, 3):
        currency = 1 # euros

    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        user.profile.currency = currency
        user.save()

    request.session['currency'] = currency

    currency_symbols = ('$', '€', '£')
    request.session['currency_symbol'] = currency_symbols[int(request.session['currency'])]

    return JsonResponse({'currency': currency})

def ajax_change_unit_system(request):
    unit_system = request.GET.get('units', 0)

    if int(unit_system) not in range(0,2) :
        unit_system = 0 # metric

    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        user.profile.unit_system = unit_system
        user.save()

    request.session['units'] = unit_system

    return JsonResponse({'units': unit_system})

@login_required
def settings(request):
    request.session['currency'] = request.user.profile.currency
    return render(request, 'account_settings/settings.html')
