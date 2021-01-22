import stripe
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.urls import reverse
from django.urls import path
from django.conf import settings
from event_crud.models import Event
from buy_ticket.models import Ticket
from django.conf.urls import url
from django.utils.translation import ngettext
from django.contrib import messages
from buy_ticket.errors import StripeError
from buy_ticket.models import Payment
from event_crud.utils import refund_all_event_users

stripe.api_key = settings.STRIPE_API_KEY

@admin.register(Event)
class Event(admin.ModelAdmin):


    list_display = ['title', 'start_date', "is_responsible", 'ticket_fee', 'end_date']
    search_fields = (
        'title', 'description', 'host__email'
    )
    actions = ['refund_company', 'refund_users']

    list_filter = ('start_date', 'end_date', 'is_responsible',
                   'is_refunded_to_host', 'all_user_payments_refunded')

    ordering = ('start_date', 'end_date', 'ticket_fee')

    def refund_company(self, request, queryset):
        amount = 0
        for i in queryset:
            if i.is_responsible:
                tickets = Ticket.objects.filter(event=i)
                if not tickets:
                    continue
                ticket_fee = 0
                for j in tickets:
                    ticket_fee += i.ticket_fee*(1-settings.CHARGE_PERCENTAGE)/100 if not j.is_vip \
                        else i.vip_ticket_fee*(1-settings.CHARGE_PERCENTAGE)/100
                try:
                    transfer = stripe.Transfer.create(
                        amount=ticket_fee,
                        currency="amd",
                        destination=i.host.stripe_id
                    )
                    i.is_refunded_to_host = True
                    i.save()
                    amount += 1
                except Exception as e:
                    self.message_user(request, ngettext(
                        '%dth event received a stripe error error.',
                        '%dth event received a stripe error error.',
                        amount,
                    ) % amount, messages.ERROR)
        self.message_user(request, ngettext(
            '%d event have successfully been transferred amount to the company.',
            '%d events have successfully been transferred amount to the company.',
            amount,
        ) % amount, messages.SUCCESS)

    def refund_users(self, request, queryset):
        amount = 0
        for i in queryset:
            if i.is_responsible:
                try:
                    refund_all_event_users(i)
                    amount += 1
                except StripeError as e:
                    self.message_user(request, ngettext(
                        '%dth event received a stripe error error.',
                        '%dth event received a stripe error error.',
                        amount,
                    ) % amount, messages.ERROR)
                except Exception as e:
                    pass
        self.message_user(request, ngettext(
            '%d event have successfully been transferred amount to the company.',
            '%d events have successfully been transferred amount to the company.',
            amount,
        ) % amount, messages.SUCCESS)

    refund_company.short_description = "Refund selected events' companies"
    refund_users.short_description = "Refund selected events' ticket buyers"

