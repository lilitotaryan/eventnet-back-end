import os

import stripe
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.views import APIView
from django.conf import settings
from authentication.permissions import ApiTokenPermission, LoggedInPermission, UserVerified
from authentication.serializers import error_many_list_serializer
from authentication.utils import response, get_current_time, send_email
from buy_ticket.errors import UserHasNoTicket, NoAvailablePlaces, UserDoesNotHavePayment, TicketIsExpired, \
    PaymentExpired, CannotPayForPassedEvent, StripeError
from buy_ticket.filters import TicketFilter
from buy_ticket.serializers import PaymentSerializer, TicketCreateSerializer, TicketUpdateSerializer
from main_app.api_exceptions import EventNotFound, TicketNotFound, PaymentNotFound, UserPermission
from event_crud.models import Event
from buy_ticket.models import Ticket, Payment
from authentication.errors import ValidationError
from subscribe.task import send_celery_email

stripe.api_key = settings.STRIPE_API_KEY

class TicketView(APIView):
    permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified]

    def get(self, request, public_id=None):
        page = request.GET.get('page', 1)
        user = request.user
        if public_id is None:
            tickets = Ticket.objects.filter(user=user)
            if tickets is not None:
                tickets = TicketFilter(request.GET, queryset=tickets).qs
                paginator = Paginator(tickets, settings.TICKET_PAGE_SIZE)
                # if int(page) > events_data.num_pages or int(page) < 1:
                #     raise NotFound
                try:
                    tickets = paginator.page(page)
                except PageNotAnInteger:
                    tickets = paginator.page(1)
                    page = 1
                except EmptyPage:
                    tickets = paginator.page(paginator.num_pages)
                    page = paginator.num_pages
                return response(data={"tickets": [i.serialize(extra_info=False) for i in tickets],
                                      "current_page": page,
                                      "last_page": paginator.num_pages,
                                      "has_next": tickets.has_next(),
                                      "has_previous": tickets.has_previous()})
            raise UserHasNoTicket()
        else:
            if public_id:
                ticket = Ticket.objects.filter(public_id=public_id).first()
                if not ticket:
                    raise TicketNotFound
                if not ticket.user == request.user:
                    raise UserPermission
                return response(data=ticket.serialize(extra_info=True))
        return response()


    def post(self, request, public_id=None):
        data = TicketCreateSerializer(data=request.data)
        if data.is_valid():
            payment = Payment.objects.filter(public_id = data.validated_data.get("payment_id")).first()
            if payment:
                if payment.user != request.user:
                    raise UserDoesNotHavePayment()
                if not data.validated_data.get("is_ok"):
                    payment.delete()
                    payment.event.available_places = payment.event.available_places + payment.quantity
                    payment.event.save()
                    return response()
                event = payment.event
                if payment.is_expired:
                    raise PaymentExpired()
                payment.end_time = get_current_time()
                payment.is_expired = True
                payment.refund_id = data.validated_data.get("refund_id")
                payment.save()
            else:
                raise PaymentNotFound
            result = []
            email_result = []
            for i in range(0, payment.quantity):
                ticket = Ticket.objects.create(user=request.user,
                                                event=event,
                                                is_vip=payment.is_vip)
                result.append(ticket.public_id)
                email_result.append(ticket)
            send_celery_email('Bought Tickets', request.user.email, settings.TICKET_TEMPLATE,
                                                                                     email_result)
            return response(data=result)
        raise ValidationError(error_list=error_many_list_serializer(data.errors))

    def put(self, request, public_id=None):
        data = TicketUpdateSerializer(data=request.data)
        if data.is_valid():
            try:
                ticket = Ticket.objects.get(public_id=data.validated_data.get('public_id'))
            except Ticket.DoesNotExist or Ticket.MultipleObjectsReturned:
                raise TicketNotFound
            if ticket.is_used or ticket.event.end_date < get_current_time():
                raise TicketIsExpired()
            if request.user != ticket.event.host:
                raise UserPermission
            ticket.is_used = True
            ticket.save()
            return response()
        raise ValidationError(error_list=error_many_list_serializer(data.errors))


class StripePayementsView(APIView):
    permission_classes = [ApiTokenPermission, LoggedInPermission, UserVerified]

    def get(self, request):
        return response()

    def post(self, request):
        data = PaymentSerializer(data=request.data)
        if data.is_valid():
            event = Event.objects.filter(public_id=data.validated_data.get("public_id")).first()
            if not event:
                raise EventNotFound
            if event.ticket_fee == 0:
                raise UserPermission
            if event.available_places < data.validated_data.get('quant'):
                raise NoAvailablePlaces()
            if event.end_date < get_current_time():
                raise CannotPayForPassedEvent()
            event.available_places = event.available_places - data.validated_data.get('quant')
            event.save()
            amount = data.validated_data.get('quant')*event.ticket_fee if not data.validated_data.get('is_vip') \
                else data.validated_data.get('quant')*event.vip_ticket_fee
            if not event.is_responsible:
                try:
                    payment_intent = stripe.PaymentIntent.create(
                        payment_method_types=['card'],
                        amount=amount*100,
                        currency='amd',
                        application_fee_amount=100*amount*settings.CHARGE_PERCENTAGE/100,
                        stripe_account=event.host.stripe_id,
                        receipt_email = settings.EMAIL_HOST_USER
                        )
                except Exception as e:
                    raise StripeError()
            else:
                try:
                    payment_intent = stripe.PaymentIntent.create(
                        payment_method_types=['card'],
                        amount=amount*100,
                        currency='amd',
                        receipt_email=settings.EMAIL_HOST_USER
                    )
                except Exception as e:
                    raise StripeError()
            payment = Payment.objects.create(amount=amount,
                                   quantity=data.validated_data.get('quant'),
                                   is_vip=data.validated_data.get('is_vip'),
                                   user = request.user,
                                   event = event)
            return response(data={"client_secret": payment_intent.client_secret,
                                  "payment_id": payment.public_id,
                                  "public_id": data.validated_data.get("public_id")
            })
        raise ValidationError(error_list=error_many_list_serializer(data.errors))



class PaymentsView(APIView):
    pass
