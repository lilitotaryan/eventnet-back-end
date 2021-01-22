import os

import stripe
from django.contrib.auth import authenticate, logout
from rest_framework.decorators import permission_classes
from rest_framework_jwt.settings import api_settings

from event_crud.permissions import CompanyUserPermission
from main_app.decorators import error_handler
from main_app.constants import SESSION_TOKEN_LEN, EMAIL_VERIFICATION_SUBJECT
from subscribe.task import send_celery_email
from .permissions import ApiTokenPermission, LoggedInPermission, \
    UserVerified, UserNotVerified, StripeLoggedInPermission
from .serializers import UserLoginSerializer, UserEmailValidationTokenSerializer, error_many_list_serializer, \
    ForgotPasswordSerializer
from rest_framework.views import APIView
from .models import Session, CustomUser
from user_crud.models import Category
from django.conf import settings
from .errors import InvalidUsernamePassword, InvalidEmailValidationToken, ValidationError, TokenIsInvalid, \
    UnexpectedError, StripeCodeIsInvalid
from user_crud.errors import CategoriesNotFound
from .utils import response, send_email, string_to_bool
from main_app.api_exceptions import NotFound

jwt_encode = api_settings.JWT_ENCODE_HANDLER

jwt_decode = api_settings.JWT_DECODE_HANDLER

jwt_payload = api_settings.JWT_PAYLOAD_HANDLER

stripe.api_key = settings.STRIPE_API_KEY


class Login(APIView):
    permission_classes = [ApiTokenPermission]

    def post(self, request):
        data = UserLoginSerializer(data=request.data)
        if not data.is_valid():
            raise ValidationError(error_list=error_many_list_serializer(data.errors))
        email = data.validated_data.get("email")
        password = data.validated_data.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:
            payload = jwt_payload(user)
            token = jwt_encode(payload)
            session = Session(token=token[len(token)-SESSION_TOKEN_LEN:], user=user,
                              device_brand=data.validated_data.get('device_brand'),
                              os_system=data.validated_data.get('os_system'))
            session.save()
            data = {
                "auth_token": token,
                "is_verified": user.is_verified,
                "is_company": user.is_company
            }
            return response(data=data)
        raise InvalidUsernamePassword()


class Logout(APIView):
    permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified]


    def get(self, request):
        expire_all = string_to_bool(request.GET.get('expire_all', False))
        session = Session.objects.get(token=request.session_token)
        if not expire_all:
            session.expire_session()
            logout(request)
            return response()
        Session.expire_all_sessions(user=request.user)
        logout(request)
        return response()



@permission_classes([ApiTokenPermission])
def get_all_categories(request):
    all_categories = Category.objects.all()
    if all_categories is not None:
        return response(data={"categories": [i.serialize() for i in all_categories]})
    raise CategoriesNotFound()


class EmailVerification(APIView):
    permission_classes = [ApiTokenPermission, LoggedInPermission, UserNotVerified]


    def get(self, request):
        user = request.user
        email_sent = string_to_bool(request.GET.get('email_sent', "False"))
        if not email_sent:
            verification_token = user.get_verification_token()
            send_celery_email(EMAIL_VERIFICATION_SUBJECT, user.email,
                       settings.EMAIL_VERIFICATION_TEMPLATE, verification_token)
            user.save()
            return response()
        else:
            verification_token = user.re_update_verification_token()
            send_celery_email(EMAIL_VERIFICATION_SUBJECT, user.email,
                       settings.EMAIL_VERIFICATION_TEMPLATE, verification_token)
            user.save()
            return response()


    def post(self, request):
        user = request.user
        token = UserEmailValidationTokenSerializer(data=request.data)
        if token.is_valid():
            if not token.check_token(user, token.validated_data):
                raise InvalidEmailValidationToken()
            user.is_verified = True
            user.save()
            return response()
        raise ValidationError(error_list=error_many_list_serializer(token.errors))


class ForgotPasswordView(APIView):
    permission_classes = [ApiTokenPermission]


    def get(self, request, ot_token=None, email=""):
        if ot_token is None:
            user = CustomUser.objects.filter(email=email).first()
            if user:
                send_celery_email('Reset Password', user.email, settings.RESET_PASSWORD_TEMPLATE, os.path.join(settings.WEB_URL,
                                                                                      "auth/forgot_password/{}/{}"
                                                                                      .format(user.generate_ot_token(),
                                                                                              email)))
            return response()
        raise NotFound


    def post(self, request, ot_token=None, email=""):
        if ot_token is not None and email:
            user = CustomUser.objects.filter(email=email).first()
            if user.get_ot_token() != ot_token:
                raise TokenIsInvalid()
            data = ForgotPasswordSerializer(data=request.data)
            if data.is_valid():
                user.set_password(data.validated_data.get('password1'))
                user.save()
                user.generate_ot_token()
                session = Session.objects.filter(user_id=user.id).first()
                session.expire_all_sessions(user)
                return response()
            raise ValidationError(error_list=error_many_list_serializer(data.errors))
        raise NotFound



class StripeAuthView(APIView):
    permission_classes = [StripeLoggedInPermission, CompanyUserPermission]

    def get(self, request):
      code = request.GET.get('code', None)
      try:
        res = stripe.OAuth.token(grant_type="authorization_code", code=code,)
      except stripe.oauth_error.OAuthError as e:
        raise StripeCodeIsInvalid()
      except Exception as e:
        print(e)
        return UnexpectedError()

      request.user.stripe_id = res["stripe_user_id"]
      request.user.save()
     # session = Session.objects.get(token=request.session_token)
     # session.expire_session()
     # payload = jwt_payload(request.user)
     # token = jwt_encode(payload)
     # session_new = Session(token=token[len(token) - SESSION_TOKEN_LEN:], user=request.user,
     #                   device_brand=session.device_brand,
     #                   os_system=session.os_system)
     # session_new.save()
      data = {
          "is_verified": request.user.is_verified,
          "is_company": request.user.is_company
      }
      # Render some HTML or redirect to a different page.
      return response(data=data)
