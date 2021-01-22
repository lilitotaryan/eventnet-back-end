from enum import Enum
from smtplib import SMTPException
import re

from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.timezone import localdate
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import JsonResponse
from django.conf import settings

from authentication.errors import UnexpectedError


class BaseEnum(Enum):
    @classmethod
    def members(cls):
        for i in cls:
            return i.value, i.name


class StateEnum(BaseEnum):
    REGISTER = 1
    UNSUCCESSFUL_REGISTER = 2
    FIRST_LOGIN = 3
    LOGIN = 4
    UNSUCCESSFUL_LOGIN = 5
    LOGOUT = 6
    RESET_PASSWORD = 7
    UPDATE_DATA = 8


def get_current_time():
    return timezone.now()


def get_current_date():
    return localdate()


def response(data="", errors="", success=True, status=200):
    return JsonResponse(data={"errors": errors,
                              "OK": success,
                              "data": data}, status=status)


def send_email(subject, to, template, value):
    try:
        subject, from_email, to = subject, settings.EMAIL_HOST_USER, [to]
        # todo customise this, add email_content location
        html_content = render_to_string(template, {'value': value})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    # todo add in logger
    except SMTPException as e:
        print(e)
        raise UnexpectedError()
    return True


def string_to_bool(value):
    value = re.sub(r"[^a-zA-Z]","", value)
    if value == "True" or value == "true" or value == "TRUE":
        return True
    elif value == "False" or value == "false" or value == "FALSE":
        return False
    else:
        return None

def string_to_int(value):
    try:
        return int(value)
    except Exception:
        return 2

