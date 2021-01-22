from main_app.errors import MainAppException


class AuthException(MainAppException):
    default_code = "authentication_error"


class ValidationErrorBase(Exception):
    code = 20
    field = ""
    message = "This field is required."
    default_code = 'validation_error'

    def __init__(self, field=None, message=""):
        if field:
            self.field = field
        if message:
            self.message = message

    def serialize(self):
        return {
            "error_field": self.field,
            "error_message": self.message,
        }


class ValidationError(ValidationErrorBase):
    code = 21
    message = "Invalid request"
    default_code = "validation_error"
    error_list = []

    def __init__(self, error_list=None):
        if error_list:
            self.error_list = error_list

    def serialize(self):
        return {
            "error_code": self.code,
            "error_fields": [e.serialize() for e in self.error_list],
            "error_message": self.message,
            "default_code": self.default_code
        }

class DeviceDataNotValid(AuthException):
    def __init__(self):
        super().__init__(code=1,
                         message='Device Data is not Valid.',
                         default_code='device_data_not_valid')


class InvalidUsernamePassword(AuthException):
    def __init__(self):
        super().__init__(code=2,
                         message='Invalid Username or Password.',
                         default_code='invalid_username_password')


class InvalidEmailValidationToken(AuthException):
    def __init__(self):
        super().__init__(code=3,
                         message='The provided validation token is either non valid or expired, '
                                 'either resend the validation email or input the valid token.',
                         default_code='invalid_email_validation_token')


class UnexpectedError(AuthException):
    def __init__(self):
        super().__init__(code=4,
                         message='Unexpected error occurred.',
                         default_code='unexpected_error')


class TokenIsInvalid(AuthException):
    def __init__(self):
        super().__init__(code=5,
                         message='Provided one time link is invalid. Please try to send email again.',
                         default_code='forgot_password_token_invalid')


class StripeCodeIsInvalid(AuthException):
    def __init__(self):
        super().__init__(code=6,
                         message='Provided Stripe authorization code is invalid.',
                         default_code='invalid_stripe_authorization_code')