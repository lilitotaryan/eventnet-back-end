from main_app.errors import MainAppException


class SubscribeException(MainAppException):
    default_code = "subscribe_error"


class EmailRequired(SubscribeException):
    def __init__(self):
        super().__init__(code=60,
                         message='Email is required for subscriber.',
                         default_code='email_is_required')


class SubscriberAlreadyExists(SubscribeException):
    def __init__(self):
        super().__init__(code=61,
                         message='Subscriber with specified email already exists.',
                         default_code='subscriber_already_exists')
