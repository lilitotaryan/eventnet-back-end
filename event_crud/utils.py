import stripe

from authentication.utils import response
from buy_ticket.errors import StripeError, EventIsNotResponsible
from buy_ticket.models import Payment
from main_app.api_exceptions import NoPaymentIsMade
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY

def refund_all_event_users(event):
    if event.is_responsible:
        payments = Payment.objects.filter(event=event, user__is_company=False)
        if not payments:
            raise NoPaymentIsMade
        for i in payments:
            try:
                refund = stripe.Refund.create(
                    payment_intent=i.refund_id,
                )
            except Exception as e:
                raise StripeError()
            i.is_refunded=True
            i.save()
        event.all_user_payments_refunded = True
        event.save()
        return response()
    raise EventIsNotResponsible()