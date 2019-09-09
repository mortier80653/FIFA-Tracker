import logging

from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext_lazy as _
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .tokens import account_activation_token, reset_password_token
from Fifa_Tracker.celery import app


@app.task(queue='quick_queue')
def send_verification_email(username, scheme, domain):
    try:
        user = User.objects.get(username=username)

        subject = _('FIFA Tracker - Account activation')
        message = render_to_string('accounts/activate_email.html', {
            'user': user,
            'scheme': scheme,   # HTTPS on prod / HTTP on local
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })

        user.email_user(subject, message)
    except User.DoesNotExist:
        logging.warning("Tried to send verification email to non-existing user '%s'" % username)


@app.task(queue='quick_queue')
def send_password_reset_email(pk, scheme, domain):
    try:
        user = User.objects.get(pk=pk)

        subject = _('FIFA Tracker - Password Reset')
        message = render_to_string('accounts/password_reset_email.html', {
            'user': user,
            'scheme': scheme,   # HTTPS on prod / HTTP on local
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': reset_password_token.make_token(user),
        })

        user.email_user(subject, message)
    except User.DoesNotExist:
        logging.warning("Tried to send password reset email not associated with any user")