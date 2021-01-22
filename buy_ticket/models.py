# Create your models here.
from django.db import models

from authentication.utils import get_current_time
from buy_ticket.utils import id_generator, PaymentReason
from event_crud.models import Event
from user_crud.models import CustomUser


class Ticket(models.Model):
    public_id = models.IntegerField(default=id_generator, unique=True, blank=False)
    user = models.ForeignKey(CustomUser, models.CASCADE, null=True)
    event = models.ForeignKey(Event, models.CASCADE, null=True)
    is_vip = models.BooleanField(default=False)
    additional_info = models.CharField(max_length=1000, blank=True)
    created_date = models.DateTimeField(default=get_current_time)
    is_used = models.BooleanField(default=False)

    def serialize(self, extra_info = True):
        data = {"public_id": self.public_id,
                "is_vip": self.is_vip,
                "created_date": self.created_date,
                "event": self.event.serialize(),
                'is_used': self.is_used}
        if extra_info:
            data["user"] = self.user.serialize()
            data["additional_info"] = self.additional_info
        return data

    def __str__(self):
        return str(self.public_id)


class Payment(models.Model):
    public_id = models.IntegerField(default=id_generator, unique=True, blank=False)
    start_time = models.DateTimeField(default=get_current_time)
    end_time = models.DateTimeField(default=get_current_time)
    amount = models.IntegerField(default=0)
    quantity = models.IntegerField(default=1)
    event = models.ForeignKey(Event, models.CASCADE, null=True)
    is_vip = models.BooleanField(default=False)
    user = models.ForeignKey(CustomUser, models.CASCADE, null=True)
    reason = models.IntegerField(choices=PaymentReason.members(), default=0)
    is_expired = models.BooleanField(default=False)
    refund_id = models.CharField(max_length=100, null=True)
    is_refunded = models.BooleanField(default=False)