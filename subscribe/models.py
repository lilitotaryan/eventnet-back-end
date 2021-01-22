from django.db import models

from authentication.utils import get_current_time
from main_app.api_exceptions import NoTicketPurchased
from subscribe.errors import EmailRequired, SubscriberAlreadyExists
from user_crud.models import CustomUser


class SubscriberManager(models.Manager):
    def create(self, **obj_data):
        is_user = True
        if obj_data.get('email'):
            try:
                self.model.objects.get(email=obj_data.get('email'))
                raise SubscriberAlreadyExists()
            except self.model.DoesNotExist or self.model.MultipleObjectsReturned:
                pass
            # try:
            #     user = CustomUser.objects.get(email=obj_data.get('email'))
            # except CustomUser.DoesNotExist or CustomUser.MultipleObjectsReturned:
            #    is_user = False
            # if is_user:
            #     obj_data['user'] = user
            return super().create(**obj_data)
        raise EmailRequired()


class Subscriber(models.Model):
    email = models.EmailField(max_length=200, blank=True, default=None, unique=True)
    last_subscription_email_date = models.DateTimeField(default=get_current_time, blank=True, null=True)
    subscription_date = models.DateTimeField(blank=True, default=get_current_time)
    amount_of_subscription_emails = models.IntegerField(default=0)
    objects = SubscriberManager()

    def __str__(self):
        return self.email

