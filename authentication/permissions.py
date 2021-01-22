from django.conf import settings

from rest_framework import permissions
from rest_framework_jwt.settings import api_settings

from .models import Session
from user_crud.models import CustomUser
from main_app.api_exceptions import InvalidHeaders, UserNotFound, NotFound, SessionAlreadyExpired
from main_app.constants import SESSION_TOKEN_LEN

import jwt

jwt_response_payload = api_settings.JWT_PAYLOAD_GET_USER_ID_HANDLER

jwt_decode = api_settings.JWT_DECODE_HANDLER

jwt_encode = api_settings.JWT_ENCODE_HANDLER


class LoggedInPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        token = request.META.get('HTTP_JWT_TOKEN')
        if token is None:
            raise InvalidHeaders
        try:
            user_id = jwt_decode(token).get("user_id", None)
        except (jwt.ExpiredSignature, jwt.DecodeError, jwt.InvalidTokenError) as e:
            if settings.DEBUG:
                print(e)
            raise InvalidHeaders
        if user_id is None:
            raise InvalidHeaders
        user = CustomUser.objects.filter(pk=user_id).first()
        session = Session.objects.filter(token=token[len(token) - SESSION_TOKEN_LEN:]).first()
        if session and user:
            if session.is_unexpired():
                request.user = user
                request.session_token = session.token
                return True
            raise SessionAlreadyExpired
        raise InvalidHeaders


class UserVerified(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_verified:
            raise UserNotFound
        return True


class UserNotVerified(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_verified:
            raise NotFound
        return True


class ApiTokenPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        api_key = request.META.get('HTTP_API_KEY')
        if api_key is not None:
            if settings.API_TOKEN == api_key:
                return True
        raise InvalidHeaders


class StripeLoggedInPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        token = request.GET.get('state', None)
        if token is None:
            raise InvalidHeaders
        try:
            user_id = jwt_decode(token).get("user_id", None)
        except (jwt.ExpiredSignature, jwt.DecodeError, jwt.InvalidTokenError) as e:
            if settings.DEBUG:
                print(e)
            raise InvalidHeaders
        if user_id is None:
            raise InvalidHeaders
        user = CustomUser.objects.filter(pk=user_id).first()
        session = Session.objects.filter(token=token[len(token) - SESSION_TOKEN_LEN:]).first()
        if session and user:
            request.user = user
            request.session_token = session.token
            return True
        raise InvalidHeaders
