import os

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def url_params(request, *args):
    request_dict = request.GET.copy()

    params = "{}{}".format(args[0], args[1])

    for param in request_dict:
        if param in args[0]:
            continue

        params += "&{field}={field_value}".format(
            field=str(param), field_value=str(request_dict[param]))

    return params.replace(',', "%2C")


@register.simple_tag
def file_timestamp(path):
    full_path = os.path.join(settings.STATIC_ROOT, path)
    if not os.path.exists(full_path):
        return 1

    return int(os.path.getmtime(full_path))
