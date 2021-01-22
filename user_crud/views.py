from rest_framework.views import APIView

from authentication.serializers import error_many_list_serializer, error_many_list_serializer
from main_app.api_exceptions import NoPaymentIsMade
from main_app.decorators import error_handler
from event_crud.utils import refund_all_event_users
from user_crud.errors import UserDataNotValid, CategoryDataNotValid, UserHasNoCategory, AddressDataNotValid, \
    UserHasNoAddress, UserHasAddress, CannotDeleteUserHavingEvents
from authentication.models import Session
from authentication.permissions import ApiTokenPermission, LoggedInPermission, UserVerified
from authentication.utils import response, get_current_time
from user_crud.models import Category, Address
from user_crud.serializers import UserRegistrationSerializer, CompanyRegistrationSerializer, UserUpdateSerializer, \
    CategoryUserSerializer, AddressSerializer, AddressSerializer, ResetPasswordSerializer
from authentication.errors import ValidationError
from user_crud.models import CustomUser
from event_crud.models import Event
from buy_ticket.models import Ticket
from buy_ticket.errors import StripeError

class User(APIView):


    def post(self, request):
        if not request.data.get("is_company"):
            data = UserRegistrationSerializer(data=request.data)
        else:
            data = CompanyRegistrationSerializer(data=request.data)
        if data.is_valid():
            user = data.create(validated_data=data.validated_data)
            if user is not None:
                return response(data=user.serialize(extra_info = True))
        raise ValidationError(error_list=error_many_list_serializer(data.errors))


    def get(self, request):
        return response(data=request.user.serialize(extra_info = True))


    def delete(self, request):
        user = request.user
        if user.is_company:
            events = Event.objects.filter(host=user, is_responsible = False, end_date__lt = get_current_time())
            if events and Ticket.objects.filter(event__in = events):
                raise CannotDeleteUserHavingEvents()
            events =  Event.objects.filter(host=user, is_responsible = True, all_user_payments_refunded=False)
            if events and Ticket.objects.filter(event__in = events):
                for i in events:
                    try:
                        refund_all_event_users(i)
                    except NoPaymentIsMade as e:
                        pass
                    except StripeError() as e:
                        raise e
                i.all_user_payments_refunded = True
            events = Event.objects.filter(host=user)
            for i in events:
                i.delete()
        Session.expire_all_sessions(user=request.user)
        user.is_active = False
        user.save()
        return response()


    def patch(self, request):
        user = request.user
        request_data = request.data
        if request_data:
            data = UserUpdateSerializer(data=request_data)
            if data.is_valid():
                user = data.update(instance=user, validated_data=data.validated_data)
                if user is not None:
                    return response()
            raise ValidationError(error_list=error_many_list_serializer(data.errors))
        raise UserDataNotValid()

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [ApiTokenPermission]
        else:
            permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified]
        return [permission() for permission in permission_classes]


class UserCategory(APIView):
    permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified]


    def post(self, request):
        # todo check validation errors
        user = request.user
        data = CategoryUserSerializer(data=request.data, user=user)
        if data.is_valid():
            data.update(user, data.validated_data)
            return response()
        raise ValidationError(error_list=error_many_list_serializer(data.errors))


    def get(self, request):
        user = request.user
        all_categories = user.categories.all()
        if all_categories is not None:
            return response(data={"categories": [i.serialize() for i in all_categories]})
        raise UserHasNoCategory()


    def delete(self, request):
        # todo check validation errors
        user = request.user
        data = CategoryUserSerializer(data=request.data, user=user)
        if data.is_valid():
            data.remove(user, data.validated_data)
            return response()
        raise ValidationError(error_list=error_many_list_serializer(data.errors))


class UserAddress(APIView):
    permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified]


    def post(self, request):
        user = request.user
        data = AddressSerializer(data=request.data)
        if data.is_valid():
            hash = data.get_hash(data.validated_data)
            address = Address.objects.filter(hash=hash)
            if not address:
                address = data.create(data.validated_data)
                user.address = address
                user.save()
                return response()
            raise UserHasAddress()
        raise ValidationError(error_list=error_many_list_serializer(data.errors))


    def get(self, request):
        user = request.user
        address = user.address
        if address is not None:
            return response(data={"address": address.serialize()})
        raise UserHasNoAddress()

    def patch(self, request):
        user = request.user
        if not request.data:
            raise AddressDataNotValid()
        data = AddressSerializer(data=request.data)
        if data.is_valid():
            address = user.address
            if address:
                address_hash = data.get_hash(data.validated_data)
                found_address = Address.objects.filter(hash=address_hash).first()
                # todo find better solution of finding all relationships
                if not (CustomUser.objects.filter(address=address) and
                        Event.objects.filter(address=address).count() > 1):
                    data.update(address, data.validated_data)
                elif not found_address:
                    address = data.create(data.validated_data)
                else:
                    address = found_address
                user.address = address
                user.save()
                return response()
            raise UserHasNoAddress()
        raise ValidationError(error_list=error_many_list_serializer(data.errors))

    # def patch(self, request):
    #     user = request.user
    #     if not request.data:
    #         raise AddressDataNotValid()
    #     data = AddressUpdateSerializer(data=request.data)
    #     if data.is_valid():
    #         address = user.address
    #         if address:
    #             data.update(address, data.validated_data)
    #             return response()
    #         raise UserHasNoAddress()
    #     raise ValidationError(error_list=error_many_list_serializer(data.errors))


    def delete(self, request):
        user = request.user
        address = user.address
        if address:
            user.address = None
            user.save()
            if not (CustomUser.objects.filter(address=address) and
                        Event.objects.filter(address=address)):
                address.delete()
            return response()
        raise UserHasNoAddress()


class ResetPassword(APIView):
    permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified]


    def post(self, request):
        ResetPasswordSerializer(data=request.data,
                                session=Session.objects.get(token=request.session_token)).validate_passwords(request.user)
        Session.expire_all_sessions(request.user)
        return response()

