import datetime
from gettext import ngettext

import geoip2.database
from django.db.models import Model
from django.urls import reverse_lazy
from django.utils.http import urlencode

from protectapp import settings
from src.core.value_object.ip_data import IpData


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_ip_data(ip: str) -> IpData:
    """
    Detects timezone based on IP address using ipinfo.io API.
    If no IP is provided, it will auto-detect your current public IP.
    """
    try:
        reader = geoip2.database.Reader(settings.IP_DATABASE_PATH)
        response = reader.city(ip)
        data = IpData(
            timezone=response.location.time_zone,
            country_code=response.country.iso_code,
            state_code=response.subdivisions.most_specific.iso_code
        )
        reader.close()

        return data
    except Exception as e:
        return IpData()


def full_url_for_route(route_name, kwargs=None, query_params=None):
    url = reverse_lazy(route_name, kwargs=kwargs)
    if query_params:
        url = url + f'?{urlencode(query_params)}'

    return f'{settings.APP_URL}{url}'


def full_url_for_path(path: str, query_params=None):
    if query_params:
        path = path + f'?{urlencode(query_params)}'

    return f'{settings.PROTOCOL}://{settings.APP_URL}{path}'


def reverse_lazy_with_query(route_name, kwargs=None, query_params: dict | None = None):
    url = reverse_lazy(route_name, kwargs=kwargs)
    if query_params:
        url = url + f'?{urlencode(query_params)}'

    return url


def reverse_lazy_admin(object: Model, action: str, args: list = None, is_full_url: bool = False):
    """
    # In general:
    admin:appname_modelname_adminroute

    # List (changelist)
    reverse_lazy("admin:library_book_changelist")

    # Add
    reverse_lazy("admin:library_book_add")

    # Change (needs object ID)
    reverse_lazy("admin:library_book_change", args=[1])

    # Delete
    reverse_lazy("admin:library_book_delete", args=[1])

    # History
    reverse_lazy("admin:library_book_history", args=[1])
    """
    route = f'admin:{object._meta.app_label}_{object._meta.model_name}_{action}'
    url = reverse_lazy(route, args=args)
    if is_full_url:
        url = f'{settings.APP_URL}{url}'
    return url


def format_datetime(date: datetime):
    now = datetime.datetime.now(datetime.timezone.utc)
    # Ensure `dt` is timezone-aware
    if date.tzinfo is None:
        date = date.replace(tzinfo=datetime.timezone.utc)

    diff = now - date
    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = seconds // 3600
    days = diff.days

    if minutes < 60:
        return ngettext('%d minute ago', '%d minutes ago', minutes) % minutes
    elif hours < 24:
        return ngettext('%d hour ago', '%d hours ago', hours) % hours
    elif days < 7:
        return ngettext('%d day ago', '%d days ago', days) % days
    else:
        return date.strftime(settings.DATE_TIME_FORMAT)
