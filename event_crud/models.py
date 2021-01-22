import uuid

import stripe
from django.db import models
from authentication.utils import get_current_time
from event_crud.errors import EventAlreadyExists
from main_app.api_exceptions import NoTicketPurchased
from user_crud.models import CustomUser, Category, Address
from django.db import IntegrityError
from buy_ticket.errors import StripeError, EventIsNotResponsible
from django.conf import settings

class Event(models.Model):
    public_id = models.UUIDField(unique=True, blank=False, default=uuid.uuid4)
    title = models.CharField(max_length=100, blank=False, default=None)
    description = models.CharField(max_length=500, blank=False, default=None)
    start_date = models.DateTimeField(blank=False, default=get_current_time())
    end_date = models.DateTimeField(blank=False, default=get_current_time())
    creation_date = models.DateTimeField(auto_now=True)
    is_responsible = models.BooleanField(default=False)
    contact_phone_number = models.CharField(max_length=100, blank=False, default=None)
    categories = models.ManyToManyField(Category, blank=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=False, default=None, null=True)
    ticket_amount = models.IntegerField(default=0)
    available_places = models.IntegerField(default=0)
    ticket_fee = models.IntegerField(default=0)
    vip_ticket_fee = models.IntegerField(default=0)
    users = models.ManyToManyField(CustomUser, blank=True, related_name="cohosts")
    host = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, related_name="host", null=True)
    is_refunded_to_host = models.BooleanField(default=False)
    all_user_payments_refunded = models.BooleanField(default=False)


    def serialize(self, extra_info = False, address=True):
        data = {
            "public_id": self.public_id,
            "title": self.title,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "ticket_fee": self.ticket_fee,
            "vip_ticket_fee": self.vip_ticket_fee,
            "available_places": self.available_places,
            "ticket_amount": self.ticket_amount
                }
        data['users'] = {}
        data['users']["companies"] = [i.serialize() for i in self.users.filter(is_company=True)] if self.users.filter(is_company=True) else []
        if address:
            data["address"] = self.address.serialize()
        if self.host:
            data['users']["companies"].append(self.host.serialize())
        if extra_info:
            data["is_responsible"] = self.is_responsible
            data["contact_phone_number"] = self.contact_phone_number
            data["category"] = [i.serialize() for i in self.categories.all()] if self.categories.all() else []

            # tickets = Ticket.objects.filter(event=self)
            # data['users']["buyers"] = [i.user.serialize() for i in tickets] if tickets else []
        return data


    def update(self, other):
        self.title = other.get("title") if other.get("title") else self.title
        self.description = other.get("description") if other.get("description") else self.description
        self.contact_phone_number = other.get("contact_phone_number") if other.get("contact_phone_number") else self.contact_phone_number,
        self.start_date = other.get("start_date") if other.get("start_date") else self.start_date,
        self.end_date = other.get("end_date") if other.get("end_date") else self.end_date
        try:
            self.save()
        except IntegrityError:
            raise EventAlreadyExists()
        return self

    def __str__(self):
        return self.title

    # def refund_company(self):
    #     if self.is_responsible:
    #         tickets = Ticket.objects.filter(event=self)
    #         if not tickets:
    #             raise NoTicketPurchased
    #         ticket_fee = 0
    #         for i in tickets:
    #             ticket_fee += i.ticket_fee * (1 - settings.CHARGE_PERCENTAGE) / 100 if not i.is_vip \
    #                 else i.vip_ticket_fee * (1 - settings.CHARGE_PERCENTAGE) / 100
    #         try:
    #             transfer = stripe.Transfer.create(
    #                 amount=ticket_fee,
    #                 currency="amd",
    #                 destination=self.host.stripe_id
    #             )
    #         except Exception as e:
    #             raise StripeError()
    #         self.is_refunded_to_host = True
    #         self.save()
    #         return "ok"
    #     raise EventIsNotResponsible()


