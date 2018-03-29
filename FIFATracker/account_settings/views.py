from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

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

    if int(unit_system) not in range(0,2):
        unit_system = 0 # metric

    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        user.profile.unit_system = unit_system
        user.save()

    request.session['units'] = unit_system

    return JsonResponse({'units': unit_system})

def ajax_change_profile_status(request):
    is_profile_public = request.GET.get('is_profile_public')

    if int(is_profile_public) not in range(0,2):
        is_profile_public = 0 # Profile is private
    else:
        is_profile_public = int(is_profile_public)

    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        user.profile.is_public = is_profile_public
        user.save()

        if is_profile_public:
            status = _("Your profile is public now.")
        else:
            status = _("Your profile is private now.")
    else:
        status = _("Failed. User not authenticated")

    return JsonResponse({'status': status})

@login_required
def settings(request):
    if request.method == 'POST':
        form_passwordchange = PasswordChangeForm(request.user, request.POST)
        if form_passwordchange.is_valid():
            user = form_passwordchange.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Your password has been changed!'))
        else:
            messages.error(request, _('Password change failed.'))
    else:
        form_passwordchange = PasswordChangeForm(request.user)

    return render(request, 'account_settings/settings.html', {'form_passwordchange': form_passwordchange,})

@login_required
def change_password(request):
    return render(request, 'account_settings/settings.html')