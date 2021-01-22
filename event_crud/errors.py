from main_app.errors import MainAppException


class EventCrudException(MainAppException):
    default_code = "event_crud_error"


class EventDataNotValid(EventCrudException):
    def __init__(self):
        super().__init__(code=16,
                         message='Event Data is not valid.',
                         default_code='event_data_not_valid')


class UserHasNoEvent(EventCrudException):
    def __init__(self):
        super().__init__(code=17,
                         message='User has no registered event.',
                         default_code='user_has_no_event')


class NoPublicIdSpecified(EventCrudException):
    def __init__(self):
        super().__init__(code=18,
                         message='No public id is specified.',
                         default_code='no_public_id_specified')


class EventDateNotValid(EventCrudException):
    def __init__(self):
        super().__init__(code=20,
                         message='Provided event date is not valid. Please, increase the interval till the event.',
                         default_code='event_date_not_valid')


class EventAlreadyExists(EventCrudException):
    def __init__(self):
        super().__init__(code=21,
                         message='Event with specified title already exists.',
                         default_code='event_already_exists')


class EventHasNoCategory(EventCrudException):
    def __init__(self):
        super().__init__(code=22,
                         message='Event has no selected categories.',
                         default_code='event_has_no_categories')


class EventHasAddress(EventCrudException):
    def __init__(self):
        super().__init__(code=23,
                         message='Event already have registered the address.',
                         default_code='event_has_address')

class EventHasNoAddress(EventCrudException):
    def __init__(self):
        super().__init__(code=24,
                         message='Event has no added address.',
                         default_code='event_has_no_address')

class EventShouldHaveAtLeastOneCategory(EventCrudException):
    def __init__(self):
        super().__init__(code=25,
                         message='Event should have at least one category.',
                         default_code='event_at_least_one_category')


class CannotDeleteEventHavingTickets(EventCrudException):
    def __init__(self):
        super().__init__(code=26,
                         message='Cannot delete event that has tickets.',
                         default_code='cannot_delete_event_having_tickets')


class UserCanBuyAtMostFreeTickets(EventCrudException):
    def __init__(self, ticket_amount):
        super().__init__(code=27,
                         message='User can buy at most {} free tickets.'.format(ticket_amount),
                         default_code='user_can_buy_at_most_free_tickets')