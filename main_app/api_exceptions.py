from django.http import JsonResponse
from rest_framework.exceptions import APIException

from authentication.errors import ValidationErrorBase, AuthException
from authentication.utils import response
from buy_ticket.errors import BuyTicketException, RefundException
from event_crud.errors import EventCrudException
from subscribe.errors import SubscribeException
from user_crud.errors import UserCrudException
from buy_ticket.errors import BuyTicketException


class EventNetAPIExceptionBase(APIException):
    code = 1
    status_code = 404
    fields = []
    default_detail = "Product is not Found."
    default_code = "api_error"

    def __init__(self, detail=None, code=None):
        super().__init__(detail, code)
        self.detail=self.serialize()

    def serialize(self):
        return {
            "error_code": self.code,
            "error_message": self.default_detail,
            "fields": self.fields,
            "translation_key": self.default_code
        }


class InvalidHeaders(EventNetAPIExceptionBase):
    code = 130
    status_code = 400
    default_detail = 'Invalid Headers are Specified.'
    default_code = 'invalid_headers'


class UserNotFound(EventNetAPIExceptionBase):
    code = 131
    status_code = 401
    default_detail = 'User is not found.'
    default_code = 'user_not_found'


class NotFound(EventNetAPIExceptionBase):
    code = 132
    status_code = 404
    default_detail = 'Not found.'
    default_code = 'not_found'


class SessionAlreadyExpired(EventNetAPIExceptionBase):
    code = 133
    status_code = 401
    default_detail = 'Session is already expired.'
    default_code = 'session_expired'


class UnExpectedError(EventNetAPIExceptionBase):
    code = 134
    status_code = 500
    default_detail = "UnExpected Error."
    default_code = "unexpected"


class EventNotFound(EventNetAPIExceptionBase):
    code = 135
    status_code = 404
    default_detail = 'Event is not found.'
    default_code = 'event_not_found'


class UserPermission(EventNetAPIExceptionBase):
    code = 136
    status_code = 403
    default_detail = 'User does not have permission to preform this action.'
    default_code = 'user_does_not_have_permission'


class CompanyNotFound(EventNetAPIExceptionBase):
    code = 137
    status_code = 401
    default_detail = 'Company with this name is not found.'
    default_code = 'company_not_found'


class InstanceDoesNotHaveCategory(EventNetAPIExceptionBase):
    code = 138
    status_code = 401
    default_detail = 'Instance does not have the category.'
    default_code = 'Instance_does_not_have_category'

class TicketNotFound(EventNetAPIExceptionBase):
    code = 139
    status_code = 404
    default_detail = 'Ticket is not found.'
    default_code = 'ticket_not_found'

class PaymentNotFound(EventNetAPIExceptionBase):
        code = 140
        status_code = 404
        default_detail = 'Payment is not found.'
        default_code = 'payment_not_found'


class NoTicketPurchased(EventNetAPIExceptionBase):
    code = 141
    status_code = 404
    default_detail = 'No ticket is purchased.'
    default_code = 'no_ticket_purchased'

class NoPaymentIsMade(EventNetAPIExceptionBase):
    code = 142
    status_code = 404
    default_detail = 'No payment is made for the event.'
    default_code = 'no_payment_is_made'


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    resp = None
    if isinstance(exc, AuthException) or isinstance(exc, UserCrudException) or isinstance(exc, ValidationErrorBase) or \
            isinstance(exc, EventCrudException) or isinstance(exc, BuyTicketException) or \
            isinstance(exc, SubscribeException) or isinstance(exc, RefundException):
        return response(errors=[exc.serialize()], success=False)
    elif isinstance(exc, APIException):
        resp = response(errors=[{"error_code": 1,
                                "error_message": exc.default_detail,
                                "fields": [],
                                "translation_key": exc.default_code}],
                                status=exc.status_code, success=False)
    # todo log exception
    else:
        print(exc)
        exc = UnExpectedError()
        resp = response(errors=[{"error_code": 1,
                                "error_message": exc.default_detail,
                                "fields": [],
                                "translation_key": exc.default_code}],
                                status=exc.status_code, success=False)
    # Now add the HTTP status code to the response.
    if resp is not None:
        resp['status_code'] = exc.status_code


    return resp