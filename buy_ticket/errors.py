from main_app.errors import MainAppException


class BuyTicketException(MainAppException):
    default_code = "buy_ticket_error"


class UserHasNoTicket(BuyTicketException):
    def __init__(self):
        super().__init__(code=40,
                         message='User has no registered ticket.',
                         default_code='user_has_no_ticket')


class NoAvailablePlaces(BuyTicketException):
    def __init__(self):
        super().__init__(code=41,
                         message='No this much available places in the event.',
                         default_code='no_available_places')


class UserDoesNotHavePayment(BuyTicketException):
    def __init__(self):
        super().__init__(code=42,
                         message='User does not possess this payment.',
                         default_code='user_does_not_have_payment')

class TicketIsExpired(BuyTicketException):
    def __init__(self):
        super().__init__(code=43,
                         message='This ticket is expired.',
                         default_code='ticket_is_expired')


class PaymentExpired(BuyTicketException):
    def __init__(self):
        super().__init__(code=44,
                         message='This payment is expired.',
                         default_code='payment_is_expired')


class CannotPayForPassedEvent(BuyTicketException):
    def __init__(self):
        super().__init__(code=45,
                         message='You cannot make payments for passed Event.',
                         default_code='cannot_pay_for_passed_event')


class StripeError(BuyTicketException):
    def __init__(self):
        super().__init__(code=46,
                         message='Stripe error occurred.',
                         default_code='stripe_error')


class RefundException(MainAppException):
    default_code = "refund_error"


class EventIsNotResponsible(RefundException):
    def __init__(self):
        super().__init__(code=50,
                         message='Event is not of type responsible.',
                         default_code='event_is_not_responsible')